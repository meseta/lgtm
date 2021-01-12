""" Validates a user from GitHub """

import os
import structlog  # type: ignore
from flask import Request, abort
from pydantic import ValidationError

import firebase_admin

#from utils.models import GitHubHookFork

CORS_HEADERS = {
    'Access-Control-Allow-Origin': 'https://lgtm.meseta.dev',
    'Access-Control-Allow-Methods': 'GET, POST',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Max-Age': '3600',
    'Access-Control-Allow-Credentials': 'true'
}

app = firebase_admin.initialize_app()

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
logger.info("Started")

def github_auth_flow(request: Request):
    """ Validates a user from github and creates user """

    # CORS headers
    if request.method == 'OPTIONS':
        return ('', 204, CORS_HEADERS)

    logger.info(request)
    # # authenticate user
    # try:
    #     user = check_auth_user()
    # except AuthError as err:
    #     logger.err("Authentication error")
    #     return abort(403, "Authentication error")

    return ("OK", 200, CORS_HEADERS)
