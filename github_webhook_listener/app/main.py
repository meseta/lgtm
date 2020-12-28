""" Listens to webhooks from GitHub """
from flask import Request, escape


def hello_world(request: Request):
    """ A hello world test """
    request_json = request.get_json(silent=True)
    name = request_json["name"]
    return "Hello {}!".format(escape(name))
