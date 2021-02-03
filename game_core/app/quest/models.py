""" Data models for quests """

from typing import Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class QuestBaseModel(BaseModel):
    stage_data: Dict[str, Any] = Field(
        default_factory=dict, title="Storage for stage data"
    )

    class Config:
        extra = "forbid"


class Difficulty(Enum):
    RESERVED = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    HACKER = 5
