""" Game core """

import os
import json
import structlog  # type: ignore
from flask import Request, abort, jsonify
from pydantic import ValidationError
from google.cloud.functions.context import Context  # type:  ignore
from google.cloud import pubsub_v1  # type:  ignore

import firebase_admin  # type:  ignore
from firebase_admin import firestore  # type:  ignore
from firebase_admin.auth import (  # type:  ignore
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)

from github import Github, BadCredentialsException

from quest_system import get_quest_by_name, QuestLoadError, FIRST_QUEST_NAME
from utils.models import NewGameData, GitHubHookFork, UserData
from utils.db_ids import create_game_id, create_quest_id
from utils.verify import verify_signature

OUR_REPO = "meseta/lgtm"
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
CREATE_GAME_TOPIC = "create_new_game"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://lgtm.meseta.dev",
    "Access-Control-Allow-Methods": "GET, POST",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Max-Age": "3600",
    "Access-Control-Allow-Credentials": "true",
}

# pubsub client
publisher = pubsub_v1.PublisherClient()
create_game_path = publisher.topic_path(GCP_PROJECT_ID, CREATE_GAME_TOPIC)

# firebase client
app = (
    firebase_admin.initialize_app()
    if not firebase_admin._apps
    else firebase_admin.get_app()
)
db = firestore.client()

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
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

    # output
    if hook_fork.repository.full_name != OUR_REPO:
        logger.error("Not our repo!", repo=hook_fork.repository.full_name)
        return jsonify(error="Invalid repo"), 400

    logger.info("Got fork", data=hook_fork.dict())

    new_game_data = NewGameData(
        source="github",
        userId=hook_fork.forkee.owner.id,
        forkUrl=hook_fork.forkee.url,
    )

    logger.info(
        "Publishing to create new game",
        path=create_game_path,
        new_game_data=new_game_data,
    )
    future = publisher.publish(create_game_path, new_game_data.json().encode())
    result = future.result()
    logger.info("Publish result", result=result)

    return jsonify(status="ok")


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
        gh_id = github.get_user().id
    except BadCredentialsException as err:
        logger.warn("Bad Github credential", err=err)
        return jsonify(error="Bad GitHub credential"), 400

    if gh_id != int(user_data.id):
        return jsonify(error="ID mismatch"), 400
    logger.info("Got github ID", gh_id=gh_id)

    # write user data
    db.collection("users").document(uid).set(
        {**user_data.dict(), "joined": firestore.SERVER_TIMESTAMP, "source": "github"}
    )

    # stats
    db.collection("system").document("stats").update(
        {"players": firestore.Increment(1)}
    )

    # find ongoing game to join
    docs = (
        db.collection("games")
        .where("userId", "==", gh_id)
        .where("source", "==", "github")
        .stream()
    )
    for doc in docs:
        logger.info("Found matching game, adding user", game_id=doc.id)
        doc.reference.set({"userUid": uid}, merge=True)

    return {"ok": True}, 200, CORS_HEADERS


def create_new_game(event: dict, context: Context) -> None:
    """ Create a new game """
    logger.info("Got create new game request", payload=event)

    # decode event
    try:
        new_game_data = NewGameData.from_event(event)
    except ValidationError as err:
        logger.error("Validation error", err=err)
        raise err

    logger.info("Resolved data", new_game_data=new_game_data)

    # Find a user with the source and userId
    docs = (
        db.collection("users")
        .where("id", "==", new_game_data.userId)
        .where("source", "==", "github")
        .stream()
    )
    userUid = None
    for doc in docs:
        userUid = doc.id
        break
    logger.info("Result of user search", userUid=userUid)

    # create game if doesn't exist
    game_id = create_game_id(new_game_data.source, new_game_data.userId)
    game_ref = db.collection("game").document(game_id)
    game = game_ref.get()
    if game.exists:
        logger.info("Game already exists", game_id=game_id)
        game_ref.set(
            {
                **new_game_data.dict(),
                "userUid": userUid,
            },
            merge=True,
        )
    else:
        logger.info("Creating new game", game_id=game_id)
        game_ref.set(
            {
                **new_game_data.dict(),
                "userUid": userUid,
                "joined": firestore.SERVER_TIMESTAMP,
            }
        )

    # create starting quest if not exist
    FirstQuest = get_quest_by_name(FIRST_QUEST_NAME)
    quest_obj = FirstQuest()

    quest_id = create_quest_id(game_id, FIRST_QUEST_NAME)
    quest_ref = db.collection("quest").document(quest_id)

    quest = quest_ref.get()
    if quest.exists:
        logger.info("Quest already exists, updating", quest_id=quest_id)

        try:
            quest_obj.load(quest.to_dict())
        except QuestLoadError as err:
            logger.error("Could not load", err=err)
            raise err

    quest_ref.set(quest_obj.get_save_data())
