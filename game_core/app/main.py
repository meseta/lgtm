""" Game core """

import structlog  # type: ignore

from environs import Env
from flask import Request, abort, jsonify
from pydantic import ValidationError
from google.cloud.functions.context import Context  # type:  ignore

from firebase_admin.auth import (  # type:  ignore
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)

from github import Github, BadCredentialsException

from quest import Quest, QuestLoadError
from user import User, Source
from game import Game
from models import UserData
from github_utils import verify_signature, GitHubHookFork

env = Env()

OUR_REPO = "meseta/lgtm"
GCP_PROJECT_ID = env("GCP_PROJECT_ID")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://lgtm.meseta.dev",
    "Access-Control-Allow-Methods": "GET, POST",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Max-Age": "3600",
    "Access-Control-Allow-Credentials": "true",
}

# firebase client

logger = structlog.get_logger().bind(version=env("APP_VERSION", "test"))
logger.info("Started", our_repo=OUR_REPO)


def github_webhook_listener(request: Request):
    """ A listener for github webhooks """

    # verify
    if not verify_signature(request):
        logger.error("Invalid signature")
        return jsonify(error="Invalid signature"), 403

    # decode
    try:
        hook_fork = GitHubHookFork.parse_raw(request.data)
    except ValidationError as err:
        logger.error("Validation error", err=err)
        return jsonify(error="Validation error"), 400
    user_id = str(hook_fork.forkee.owner.id)

    # check repo is ours
    if hook_fork.repository.full_name != OUR_REPO:
        logger.error("Not our repo!", repo=hook_fork.repository.full_name)
        return jsonify(error="Invalid repo"), 400

    logger.info("Got fork", data=hook_fork.dict())

    # create a user reference, and then create new game
    user = User.find_by_source_id(Source.GITHUB, user_id)
    if not user:
        user = User.reference(Source.GITHUB, user_id)

    game = Game.new(user, hook_fork.forkee.url)
    logger.info("Created new game for user", game=game, user=user)

    return jsonify(status="ok", user_id=user_id)


def github_auth_flow(request: Request):
    """ Validates a user from github and creates user """

    # CORS headers
    if request.method == "OPTIONS":
        return ("", 204, CORS_HEADERS)

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

    # decode
    try:
        user_data = UserData.parse_raw(request.data)
    except ValidationError as err:
        logger.warn("Validation error", err=err)
        return jsonify(error="Validation error"), 400
    logger.info("Got user data", user_data=user_data)

    # authenticate GitHub
    github = Github(user_data.accessToken)

    try:
        user_id = github.get_user().id
    except BadCredentialsException as err:
        logger.warn("Bad Github credential", err=err)
        return jsonify(error="Bad GitHub credential"), 400

    if user_id != int(user_data.id):
        return jsonify(error="ID mismatch"), 400
    logger.info("Got github ID", user_id=user_id)

    # create new user, and find existing game to assign uid to
    user = User.new(uid=uid, source=Source.GITHUB, user_data=user_data)
    game = Game.find_by_user(user)
    if game:
        game.assign_to_uid(uid)
    logger.info("Results creating new user and finding game", game=game, user=user)

    return {"ok": True}, 200, CORS_HEADERS
