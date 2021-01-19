""" Verify the GitHub webhook secret """
import os
import hmac
import hashlib

from flask import Request

WEBHOOK_SECRET = bytes(os.environ["WEBHOOK_SECRET"], "utf-8")


def verify_signature(request: Request) -> bool:
    """ Validates the github webhook secret. Will return false if secret not provided """
    expected_signature = hmac.new(
        key=WEBHOOK_SECRET, msg=request.data, digestmod=hashlib.sha256
    ).hexdigest()
    incoming_signature = request.headers.get("X-Hub-Signature-256", "").removeprefix(
        "sha256="
    )
    return hmac.compare_digest(incoming_signature, expected_signature)
