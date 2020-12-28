""" Verify the GitHub webhook secret """
import os
import hmac
import hashlib

from flask import Request

SECRET = bytes(os.environ["SECRET"], "utf-8")


def verify_signature(request: Request) -> bool:
    """ Validates the github webhook secret. Will return false if secret not provided """
    expected_signature = hmac.new(
        key=SECRET, msg=request.data, digestmod=hashlib.sha256
    ).hexdigest()
    incoming_signature = request.headers.get("X-Hub-Signature-256", "").removeprefix(
        "sha256="
    )
    return hmac.compare_digest(incoming_signature, expected_signature)
