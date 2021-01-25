""" Verify the GitHub webhook secret """

import hmac
import hashlib

from environs import Env
from flask import Request

from .models import GitHubHookFork

env = Env()

WEBHOOK_SECRET = env("WEBHOOK_SECRET")
OUR_REPO = env("OUR_REPO", "meseta/lgtm")


def verify_signature(request: Request) -> bool:
    """ Validates the github webhook secret. Will return false if secret not provided """
    expected_signature = hmac.new(
        key=WEBHOOK_SECRET.encode(), msg=request.data, digestmod=hashlib.sha256
    ).hexdigest()
    incoming_signature = request.headers.get("X-Hub-Signature-256", "").removeprefix(
        "sha256="
    )
    return hmac.compare_digest(incoming_signature, expected_signature)


def check_repo_ours(hook_fork: GitHubHookFork) -> str:
    """ Check repo is valid and return the forked URL """
    return hook_fork.repository.full_name == OUR_REPO
