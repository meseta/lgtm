""" Game core """

import os
import structlog  # type: ignore
from google.cloud.functions.context import Context

import firebase_admin
from firebase_admin import firestore

from utils.models import NewGameData

FIRST_QUEST = "level0:intro"

app = firebase_admin.initialize_app()
db = firestore.client()

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
logger.info("Started")


def create_new_game(event: dict, context: Context):
    """ Create a new game """
    logger.info("Got create new game request", event=event)

    # decode event
    new_game_data = NewGameData.parse_event(event)
    logger.info("Resolved data", new_game_data=new_game_data)

    # create game if doesn't exist
    game_ref = db.collection("game").document(game_id)
    game = game_ref.get()
    if game.exists:
        logger.info("Game already exists", game_id=game_id)
        game_ref.set(
            {
                **new_game_data.dict(),
            },
            merge=True,
        )
    else:
        logger.info("Creating new game", game_id=game_id)
        game_ref.set(
            {
                **new_game_data.dict(),
                "joined": firestore.SERVER_TIMESTAMP,
            }
        )

    # create starting quest if not exist
    quest_id = f"{game_id}:{FIRST_QUEST}"
    quest_ref = db.collection("quest").document(quest_id)

    quest = quest_ref.get()
    if quest.exists:
        logger.info("Quest already exists", quest_id=quest_id)
    else:
        logger.info("Creating new quest", quest_id=quest_id)
        game_ref.set(
            {
                **new_game_data.dict(),
                "joined": firestore.SERVER_TIMESTAMP,
            }
        )
