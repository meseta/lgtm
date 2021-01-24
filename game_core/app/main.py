""" Game core """


import structlog  # type: ignore
from environs import Env

from flask import Request
from flask_cors import cross_origin

from firebase_admin.auth import (  # type:  ignore
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)
from github import Github, BadCredentialsException

from github_utils import verify_signature, check_repo_ours, GitHubHookFork
from quest import Quest
from user import User, NoUser, Source
from game import Game, NoGame

from models import UserData, StatusReturn
from framework import inject_pydantic_parse

env = Env()
CORS_ORIGIN = env("CORS_ORIGIN", "https://lgtm.meseta.dev")

logger = structlog.get_logger(__name__).bind(version=env("APP_VERSION", "test"))
logger.info("Started")


@inject_pydantic_parse
def github_webhook_listener(request: Request, hook_fork: GitHubHookFork):
    """ A listener for github webhooks """

    # verify
    if not verify_signature(request):
        logger.error("Invalid signature")
        return StatusReturn(error="Invalid signature", http_code=403)

    # decode and check it's ours
    if not check_repo_ours(hook_fork):
        logger.error("Not our repo!", repo=hook_fork.repository.full_name)
        return StatusReturn(error="Invalid repo", http_code=404)

    logger.info("Got fork", data=hook_fork.dict())
    user_id = str(hook_fork.forkee.owner.id)
    fork_url = hook_fork.forkee.url

    # create a user reference, and then create new game
    user = User.find_by_source_id(Source.GITHUB, user_id)
    if user is NoUser:
        user = User.reference(Source.GITHUB, user_id)

    game = Game.new(user, fork_url)
    logger.info("Created new game for user", game=game, user=user)

    return StatusReturn(success=True)


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
        return StatusReturn(error="Authentication error", http_code=403)
    uid = decoded_token["uid"]
    logger.info("Got authenticated user", decoded_token=decoded_token, uid=uid)

    # authenticate GitHub
    github = Github(user_data.accessToken)
    try:
        user_id = github.get_user().id
    except BadCredentialsException as err:
        logger.warn("Bad Github credential", err=err)
        return StatusReturn(error="Bad GitHub credential", http_code=400)

    if str(user_id) != user_data.id:
        return StatusReturn(error="ID mismatch", http_code=403)
    logger.info("Got github ID", user_id=user_id)

    # create new user, and find existing game to assign uid to
    user = User.new(uid=uid, source=Source.GITHUB, user_data=user_data)
    game = Game.find_by_user(user)
    if game is not NoGame:
        game.assign_to_uid(uid)
    logger.info("Results creating new user and finding game", game=game, user=user)

    return StatusReturn(success=True)
