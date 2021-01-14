""" Game core """

import os
import structlog  # type: ignore
from google.cloud.functions.context import Context

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
logger.info("Started")

def game_core(event: dict, context: Context):
    """ Game core """
    pass