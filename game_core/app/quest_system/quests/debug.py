""" The intro quest """

from ..quest_system import Quest, Difficulty

quest = Quest(
    name="debug",
    version="1.0.0",
    difficulty=Difficulty.RESERVED,
    description="This is a quest to facilitate testing/debugging",
    default_data={"a": 1},
)
