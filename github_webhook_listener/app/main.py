""" Listens to webhooks from GitHub """

import os
import json
import structlog  # type: ignore
from flask import Request, abort, jsonify
from pydantic import ValidationError

from google.cloud import pubsub_v1
import firebase_admin
from firebase_admin import firestore

from utils.verify import verify_signature
from utils.models import GitHubHookFork

OUR_REPO = "meseta/lgtm"
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
CREATE_GAME_TOPIC = "create_new_game"

# pubsub client
publisher = pubsub_v1.PublisherClient()
create_game_path = publisher.topic_path(GCP_PROJECT_ID, CREATE_GAME_TOPIC)

# firebase client
app = firebase_admin.initialize_app()
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
        logger.error("Not our repo!", repo=hook_fork.repository.full_nam)
        return jsonify(error="Invalid repo"), 400

    logger.info("Got fork", data=hook_fork.dict())

    # Find a user with the source and userId
    docs = (
        db.collection("users")
        .where("id", "==", hook_fork.forkee.owner.id)
        .where("source", "==", "github")
        .stream()
    )
    uid = None
    for doc in docs:
        uid = doc.id
        break
    logger.info("Result of user search", uid=uid)

    payload = {  # this format is from game_core/app/utils/models.py:NewGameData should unify this some day...
        "source": "github",
        "userId": hook_fork.forkee.owner.id,
        "userUid": uid,
        "forkUrl": hook_fork.forkee.url,
    }
    logger.info("Publishing to create new game", path=create_game_path, payload=payload)
    future = publisher.publish(create_game_path, json.dumps(payload).encode())
    result = future.result()
    logger.info("Publish result", result=result)

    return jsonify(status="ok")
