""" Validates a user from GitHub """

import os
import structlog  # type: ignore
from flask import Request, abort

import firebase_admin
from firebase_admin.auth import (
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)

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

    # authenticate user
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    try:
        decoded_token = verify_id_token(token)
    except (ValueError, InvalidIdTokenError, ExpiredIdTokenError, RevokedIdTokenError) as err:
        logger.warn("Authentication error", err=err)
        return abort(403, "Authentication error")



    return ("OK", 200, CORS_HEADERS)
