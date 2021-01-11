""" Game core """

import os
import structlog  # type: ignore
from google.cloud.functions import Context

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
logger.info("Started", our_repo=OUR_REPO)

def game_core(event: dict, context: Context):
    """ Game core """
    pass