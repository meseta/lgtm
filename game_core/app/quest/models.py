""" Data models for quests """

from enum import Enum
from pydantic import BaseModel, Field


class QuestBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class Difficulty(Enum):
    RESERVED = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    HACKER = 5
