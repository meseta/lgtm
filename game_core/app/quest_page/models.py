""" Data models for quests """

from typing import List
from pydantic import BaseModel, Field


class QuestData(BaseModel):
    quest_name: str = Field("", title="Name of the Quest")
    version: str = Field("", title="Version number to control loading")
    completed_stages: List[str] = Field([], title="List of completed stage names")
    serialized_data: str = Field("", title="Serialized save data")
    complete: bool = Field(False, title="Whether quest is completed")
