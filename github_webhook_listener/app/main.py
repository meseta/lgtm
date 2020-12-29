""" Listens to webhooks from GitHub """

import structlog  # type: ignore
from flask import Request, abort
from pydantic import ValidationError

from utils.verify import verify_signature
from utils.models import GitHubHookFork

logger = structlog.get_logger()

OUR_REPO = "meseta/lgtm"


def github_webhook_listener(request: Request):
    """ A listener for github webhooks """

    # verify
    if not verify_signature(request):
        return abort(403, "Invalid signature")

    # decode
    try:
        hook_fork = GitHubHookFork.parse_raw(request.data)
    except ValidationError as err:
        logger.err("Validation error", err=err)
        return abort(400, "Validation error")

    # output
    if hook_fork.repository.full_name == OUR_REPO:
        logger.info("Got fork", data=hook_fork.dict())

    return "OK"
