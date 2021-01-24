""" Sentinels """

from pydantic import BaseModel


class NoData(BaseModel):
    """ Empty class used for when no data is loaded """


class NoQuest:
    """ Empty class used for when no quest """
