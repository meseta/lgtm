# """ Base Classes for quest stage objects """

from __future__ import annotations

from typing import List, Optional, ClassVar, Any, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod
import operator
from datetime import timedelta, datetime

from structlog import get_logger

from character import Character

logger = get_logger(__name__)

if TYPE_CHECKING:
    from .quest import Quest  # pragma: no cover


class Stage(ABC):
    """A stage holds the quest stage, the execution flow is:

    stage = Stage()
    stage.prepare()
    if stage.condition():
        stage.execute()
        if stage.is_done():
            ...

    """

    @property
    @abstractmethod
    def children(cls) -> List[str]:
        """ List of children nodes of this stage """
        return NotImplemented

    def prepare(self) -> None:
        """ Any preparation for the stage """
        return

    def condition(self) -> bool:
        """ Function that will decide whether to execute """
        return True

    def execute(self) -> None:
        """ Run the stage """
        return

    def is_done(self) -> bool:
        """ Returns whether quest was completed """
        return True

    def __init__(self, quest: Quest):
        self.quest = quest

    def set_stage_data(self, value: Any):
        """ Sets stage data """
        self.quest.quest_data.stage_data[self.__class__.__name__] = value

    def get_stage_data(self, default: Any = None) -> Any:
        """ Gets stage data """
        return self.quest.quest_data.stage_data.get(self.__class__.__name__, default)

    def __repr__(self):
        return f"{self.__class__.__name__}(quest={repr(self.quest)})"


class DebugStage(Stage):
    """ For debugging purposes """

    def prepare(self) -> None:
        """ Print for debug purposes """
        logger.info(f"DEBUG STAGE PREPARE OF {self.quest}")

    def execute(self) -> None:
        """ Print for debug purposes """
        logger.info(f"DEBUG STAGE EXECUTE OF {self.quest}")


class ConditionStage(Stage):
    """ For conditional branch execution """

    @property
    @abstractmethod
    def variable(cls) -> str:
        """ Name of the variable to check """
        return NotImplemented

    # the variable to check against
    compare_variable: ClassVar[Optional[str]] = None

    # the value to check against, if compare_variable is None
    compare_value: ClassVar[Any] = None

    # the operator to use comparison on
    operator: ClassVar[Callable[..., bool]] = operator.eq

    def condition(self) -> bool:
        value_left = getattr(self.quest.quest_data, self.variable)

        if self.compare_variable is not None:
            value_right = getattr(self.quest.quest_data, self.compare_variable)
        else:
            value_right = self.compare_value

        retval = self.operator(value_left, value_right)
        logger.info(
            f"Condition stage",
            value_left=value_left,
            value_right=value_right,
            op=self.operator,
            retval=retval,
        )
        return retval


class DelayStage(Stage):
    """ For enacting a time delay """

    # how much time to delay
    delay: timedelta

    def prepare(self) -> None:
        """ On first run, insert datetime """
        if self.get_stage_data() is None:
            now = datetime.now().timestamp()
            logger.info(f"Delay stage prepare", now=now)
            self.set_stage_data(now)

    def condition(self) -> bool:
        """ Calculate whether that has elapsed """
        target = datetime.utcfromtimestamp(self.get_stage_data(0)) + self.delay
        now = datetime.now()
        logger.info(f"Delay stage prepare", now=now, target=target)
        return now > target


class FinalStage(Stage):
    """ For ending the quest """

    def __init_subclass__(cls):
        cls.children = []

    def execute(self) -> None:
        self.quest.quest_page.mark_quest_complete()
        logger.info(f"Final stage")


class CreateIssueStage(Stage):
    """ This stage posts a new issue to a user's fork """

    # which character will post the issue
    character: ClassVar[Character]

    @abstractmethod
    def create_message(cls) -> str:
        """ Should return the message to be posted """
        return NotImplemented

    def execute(self) -> None:
        """ Post the issue to the fork """
        # self.character.create_issue(self.quest)

        logger.info("Creating issue")
