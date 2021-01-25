""" Extra functions for execution environment Functions framework """

from typing import get_type_hints

from pydantic import ValidationError
import structlog  # type: ignore
from flask import Request, jsonify

from app.models import StatusReturn

logger = structlog.get_logger(__name__)


def inject_pydantic_parse(func):
    """ Wrap method with pydantic dependency injection """

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
