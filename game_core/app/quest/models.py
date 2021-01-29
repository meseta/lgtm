""" Data models for quests """

from typing import List
from enum import Enum
from pydantic import BaseModel, Field


class QuestBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class StorageModel(QuestBaseModel):
    version: str = Field(..., title="Version number to control loading")
    completed_stages: List[str] = Field([], title="List of completed stage names")
    serialized_data: str = Field(..., title="Serialized save data")
    complete: bool = Field(False, title="Whether quest is completed")


class Difficulty(Enum):
    RESERVED = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    HACKER = 5
