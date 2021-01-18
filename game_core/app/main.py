""" Game core """

import os
import structlog  # type: ignore
from pydantic import ValidationError
from google.cloud.functions.context import Context  # type:  ignore

import firebase_admin  # type:  ignore
from firebase_admin import firestore  # type:  ignore

from quest_system import get_quest_by_name, QuestLoadError, FIRST_QUEST_NAME
from utils.models import NewGameData
from utils.db_ids import create_game_id, create_quest_id

app = firebase_admin.initialize_app()
db = firestore.client()

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
logger.info("Started")


def create_new_game(event: dict, context: Context):
    """ Create a new game """
    logger.info("Got create new game request", payload=event)

    # decode event
    try:
        new_game_data = NewGameData.parse_obj(event)
    except ValidationError as err:
        logger.error("Validation error", err=err)
        raise err

    logger.info("Resolved data", new_game_data=new_game_data)

    # create game if doesn't exist
    game_id = create_game_id(new_game_data.source, new_game_data.userId)
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
