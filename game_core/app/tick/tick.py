""" Metadata pertaining to ticks/game loop execution """

from enum import Enum
from pydantic import BaseModel, Field


class TickType(Enum):
    FAST = "FAST"
    FULL = "FULL"


class TickEvent(BaseModel):
    """ Model for ticks """

    tick_type: TickType = Field(..., title="Type of tick")
