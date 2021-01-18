""" Validates a user from GitHub """

import os
import structlog  # type: ignore
from flask import Request, abort, jsonify
from pydantic import ValidationError
from github import Github, BadCredentialsException

import firebase_admin
from firebase_admin.auth import (
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)
from firebase_admin import firestore


from utils.models import UserData

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://lgtm.meseta.dev",
    "Access-Control-Allow-Methods": "GET, POST",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
    "Access-Control-Max-Age": "3600",
    "Access-Control-Allow-Credentials": "true",
}

app = firebase_admin.initialize_app()
db = firestore.client()

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
logger.info("Started")


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
    logger.info("Got authenticated user", decoded_token=decoded_token)

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
    db.collection("users").document(decoded_token["uid"]).set(
        {**user_data.dict(), "joined": firestore.SERVER_TIMESTAMP}
    )

    # stats
    db.collection("system").document("stats").update(
        {"players": firestore.Increment(1)}
    )

    # TODO: find ongoing game to join

    return {"ok": True}, 200, CORS_HEADERS
