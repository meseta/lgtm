""" Listens to webhooks from GitHub """

import os
import structlog  # type: ignore
from flask import Request, abort, jsonify
from pydantic import ValidationError

from utils.verify import verify_signature
from utils.models import GitHubHookFork

OUR_REPO = "meseta/lgtm"

logger = structlog.get_logger().bind(version=os.environ.get("APP_VERSION", "test"))
logger.info("Started", our_repo=OUR_REPO)


def github_webhook_listener(request: Request):
    """ A listener for github webhooks """

    # verify
    if not verify_signature(request):
        logger.err("Invalid signature")
        return jsonify(error="Invalid signature"), 403

    # decode
    try:
        hook_fork = GitHubHookFork.parse_raw(request.data)
    except ValidationError as err:
        logger.err("Validation error", err=err)
        return jsonify(error="Validation error"), 400

    # output
    if hook_fork.repository.full_name == OUR_REPO:
        logger.info("Got fork", data=hook_fork.dict())

        # TODO: create new game

        # TODO: link game to user if found

    return jsonify(status="ok")
