""" Extra functions for execution environment Functions framework """

from typing import get_type_hints
from base64 import b64decode

from pydantic import ValidationError
import structlog  # type: ignore
from flask import Request, jsonify
from google.cloud.functions.context import Context  # type:  ignore

from app.models import StatusReturn

logger = structlog.get_logger(__name__)


def inject_http_model(func):
    """ Wrap method with pydantic dependency injection for HTTP functions """

    def wrapper(request: Request):
        kwargs = {}
        for arg_name, arg_type in get_type_hints(func).items():
            parse_raw = getattr(arg_type, "parse_raw", None)
            if callable(parse_raw):
                try:
                    kwargs[arg_name] = parse_raw(request.data)
                except ValidationError as err:
                    logger.error("Validation error", err=err)
                    retval = StatusReturn(error="Validation error", http_code=400)
                    break

                logger.info(
                    "Decoded model and injected",
                    model=arg_type.__name__,
                    func=func.__name__,
                )
        else:
            retval = func(request, **kwargs)
            logger.info("Function run with type return", type=type(retval))

        # if isinstance(retval, StatusReturn):
        logger.info("StatusReturn with code", retval=retval, code=retval.http_code)
        return jsonify(**retval.dict()), retval.http_code
        # return retval

    return wrapper


def inject_pubsub_model(func):
    """ Wrap method with pydantic dependency injection for PubSub functions """

    def wrapper(event: dict, context: Context):
        kwargs = {}
        for arg_name, arg_type in get_type_hints(func).items():
            parse_raw = getattr(arg_type, "parse_raw", None)
            if callable(parse_raw):
                try:
                    kwargs[arg_name] = parse_raw(
                        b64decode(event["data"]).decode("utf-8")
                    )
                except ValidationError as err:
                    raise StatusReturn(error=f"Validation error {err}", http_code=400)

                logger.info(
                    "Decoded model and injected",
                    model=arg_type.__name__,
                    func=func.__name__,
                )

        return func(**kwargs)

    return wrapper
