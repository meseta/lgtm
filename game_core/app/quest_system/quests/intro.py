""" The intro quest """

from ..quest_system import Quest, Difficulty

quest = Quest(
    name="intro",
    version="0.1.0",
    difficulty=Difficulty.BEGINNER,
    description="The intro quest",
    default_data={},
)
