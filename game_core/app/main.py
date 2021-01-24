""" Game core """

from typing import get_type_hints

import structlog  # type: ignore
from environs import Env

from flask import Request, jsonify
from flask_cors import cross_origin
from pydantic import ValidationError

from functions_framework import errorhandler
from google.cloud.functions.context import Context  # type:  ignore
from firebase_admin.auth import (  # type:  ignore
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)
from github import Github, BadCredentialsException

from github_utils import verify_signature, check_repo_ours, GitHubHookFork
from quest import Quest, QuestLoadError
from user import User, Source
from game import Game
from models import UserData

env = Env()

GCP_PROJECT_ID = env("GCP_PROJECT_ID")
OUR_REPO = env("OUR_REPO", "meseta/lgtm")
CORS_ORIGIN = env("CORS_ORIGIN", "https://lgtm.meseta.dev")

logger = structlog.get_logger().bind(version=env("APP_VERSION", "test"))
logger.info("Started")


@errorhandler(ValidationError)
def validation_error(err: ValidationError):
    """ Handler for pydantic validation errors (usuall http payload) """
    logger.error("Validation error", err=err)
    return jsonify(error="Validation error"), 400


def inject_pydantic_parse(func):
    """ Wrap method with pydantic dependency injection """

    def wrapper(request: Request):
        kwargs = {}
        for arg_name, arg_type in get_type_hints(func).items():
            parse_raw = getattr(arg_type, "parse_raw", None)
            if callable(parse_raw):
                kwargs[arg_name] = parse_raw(request.data)
                logger.info(
                    "Decoded model and injected",
                    model=arg_type.__name__,
                    func=func.__name__,
                )

        return func(request, **kwargs)

    return wrapper


@inject_pydantic_parse
def github_webhook_listener(request: Request, hook_fork: GitHubHookFork):
    """ A listener for github webhooks """

    # verify
    if not verify_signature(request):
        logger.error("Invalid signature")
        return jsonify(error="Invalid signature"), 403

    # decode and check it's ours
    if not check_repo_ours(hook_fork):
        logger.error("Not our repo!", repo=hook_fork.repository.full_name)
        return jsonify(error="Invalid repo"), 404

    logger.info("Got fork", data=hook_fork.dict())
    user_id = str(hook_fork.forkee.owner.id)
    fork_url = hook_fork.forkee.url

    # create a user reference, and then create new game
    user = User.find_by_source_id(Source.GITHUB, user_id)
    if not user:
        user = User.reference(Source.GITHUB, user_id)

    game = Game.new(user, fork_url)
    logger.info("Created new game for user", game=game, user=user)

    return jsonify(status="ok", user_id=user_id)


@cross_origin(
    origins=CORS_ORIGIN,
    headers=["Authorization", "Content-Type"],
    supports_credentials=True,
)
@inject_pydantic_parse
def github_auth_flow(request: Request, user_data: UserData):
    """ Validates a user from github and creates user """

    # authenticate user
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    try:
        decoded_token = verify_id_token(token)
    except (
        ValueError,
        InvalidIdTokenError,
        ExpiredIdTokenError,
        RevokedIdTokenError,
    ) as err:
        logger.warn("Authentication error", err=err)
        return jsonify(error="Authentication error"), 403
    uid = decoded_token["uid"]
    logger.info("Got authenticated user", decoded_token=decoded_token, uid=uid)

    # authenticate GitHub
    github = Github(user_data.accessToken)
    try:
        user_id = github.get_user().id
    except BadCredentialsException as err:
        logger.warn("Bad Github credential", err=err)
        return jsonify(error="Bad GitHub credential"), 400

    if str(user_id) != user_data.id:
        return jsonify(error="ID mismatch"), 403
    logger.info("Got github ID", user_id=user_id)

    # create new user, and find existing game to assign uid to
    user = User.new(uid=uid, source=Source.GITHUB, user_data=user_data)
    game = Game.find_by_user(user)
    if game:
        game.assign_to_uid(uid)
    logger.info("Results creating new user and finding game", game=game, user=user)

    return {"ok": True}, 200
