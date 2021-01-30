""" Game core """

import structlog  # type: ignore
from environs import Env

from flask import Request
from flask_cors import cross_origin  # type:  ignore

from firebase_admin.auth import (  # type:  ignore
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)
from github import Github, BadCredentialsException

from github_utils import verify_signature, check_repo_ours, GitHubHookFork
from user import User, Source
from game import Game
from quest import Quest
from models import UserData, StatusReturn, TickEvent
from framework import inject_http_model, inject_pubsub_model

env = Env()
CORS_ORIGIN = env("CORS_ORIGIN", "https://lgtm.meseta.dev")

logger = structlog.get_logger(__name__).bind(version=env("APP_VERSION", "test"))
logger.info("Started")


@inject_http_model
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

    # fetch a user (or create new one), and then create new game
    user = User.from_source_id(source=Source.GITHUB, user_id=user_id)
    game = Game.new_from_fork(user, fork_url)

    logger.info("Created new game for user, executing", game=game, user=user)
    game.start_first_quest()

    logger.info("Done executing")

    return StatusReturn(success=True)


@cross_origin(
    origins=CORS_ORIGIN,
    headers=["Authorization", "Content-Type"],
    supports_credentials=True,
)
@inject_http_model
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
        user_id = str(github.get_user().id)
    except BadCredentialsException as err:
        logger.warn("Bad Github credential", err=err)
        return StatusReturn(error="Bad GitHub credential", http_code=400)

    if user_id != user_data.id:
        return StatusReturn(error="ID mismatch", http_code=403)
    logger.info("Got github ID", user_id=user_id)

    # create new user if it doesn't exist, and find existing game to assign uid to
    user = User.new_from_data(uid=uid, source=Source.GITHUB, user_data=user_data)

    game = Game.from_user(user)
    if isinstance(game, Game):
        game.assign_to_uid(uid)

    logger.info("Results creating new user and finding game", game=game, user=user)

    return StatusReturn(success=True)


@inject_pubsub_model
def tick(tick_event: TickEvent):
    """ Game tick """
    logger.info("Tick", source=tick_event.source)

    for quest in Quest.iterate_all():
        logger.info("Executing quest", quest=quest)
        quest.load()
        quest.execute_stages()
        quest.save()
