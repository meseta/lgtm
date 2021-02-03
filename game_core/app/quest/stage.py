# """ Base Classes for quest stage objects """

from __future__ import annotations

from typing import List, Optional, ClassVar, Any, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod
import operator
from datetime import timedelta, datetime
from re import Pattern
import random

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

    def fast_condition(self) -> bool:
        """ Fast condition checks """
        return self.condition()

    def execute(self) -> None:
        """ Run the stage """
        return

    def fast_execute(self) -> None:
        self.execute()

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

    def fast_execute(self) -> None:
        """ Print for debug purposes """
        logger.info(f"DEBUG STAGE FAST_EXECUTE OF {self.quest}")


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

    @property
    @abstractmethod
    def delay(cls) -> timedelta:
        """ how much time to delay """
        return NotImplemented

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
        self.set_stage_data(datetime.now().timestamp())


class CreateIssueStage(Stage):
    """ This stage posts a new issue to a user's fork """

    @property
    @abstractmethod
    def character(cls) -> Character:
        """ Which character will post the issue """
        return NotImplemented

    @property
    @abstractmethod
    def issue_title(cls) -> str:
        """ Issue title """
        return NotImplemented

    @property
    @abstractmethod
    def issue_body(cls) -> str:
        """ Issue main body """
        return NotImplemented

    # variable to store resulting issue ID in for later
    issue_id_variable: Optional[int] = None

    def execute(self) -> None:
        """ Post the issue to the fork """
        game = self.quest.quest_page.game
        game.load()
        fork_url = game.data.fork_url

        logger.info("Creating issue", title=self.issue_title, fork_url=fork_url)
        issue_id = self.character.issue_create(
            fork_url, self.issue_title, self.issue_body
        )

        if self.issue_id_variable:
            logger.info(
                "Storing issue Id in variable",
                issue_id=issue_id,
                variable=self.issue_id_variable,
            )
            setattr(self.quest.quest_data, self.issue_id_variable, issue_id)


class CreateIssueCommentsStage(Stage):
    """ This stage posts a comment to an existing issue to a user's fork """

    @property
    @abstractmethod
    def character(cls) -> Character:
        """ Which character will post the comment """
        return NotImplemented

    @property
    @abstractmethod
    def issue_id_variable(cls) -> int:
        """ Variable containing the ID of the issue to use """
        return NotImplemented

    @property
    @abstractmethod
    def comment_body(cls) -> str:
        """ Issue main body """
        return NotImplemented

    # variable to store resulting comment ID in for later
    comment_id_variable: Optional[str] = None

    # variable to store datetime of comment
    comment_datetime_variable: Optional[str] = None

    def execute(self) -> None:
        """ Post the issue to the fork """
        game = self.quest.quest_page.game
        game.load()
        fork_url = game.data.fork_url

        issue_id = getattr(self.quest.quest_data, self.issue_id_variable)

        logger.info("Creating comment", issue_id=issue_id, fork_url=fork_url)
        comment_id = self.character.issue_comment_create(
            fork_url, issue_id, self.comment_body
        )

        if self.comment_id_variable:
            logger.info(
                "Storing comment Id in variable",
                comment_id=comment_id,
                variable=self.comment_id_variable,
            )
            setattr(self.quest.quest_data, self.comment_id_variable, comment_id)

        if self.comment_datetime_variable:
            setattr(
                self.quest.quest_data, self.comment_datetime_variable, datetime.now()
            )


class CreateIssueConversationStage(Stage):
    """ This stage posts multiple comment to an existing issue to a user's fork """

    @property
    @abstractmethod
    def character_comment_pairs(cls) -> List[Tuple[Character, str]]:
        """ Pairs of characters and comments to post """
        return NotImplemented

    @property
    @abstractmethod
    def issue_id_variable(cls) -> int:
        """ Variable containing the ID of the issue to use """
        return NotImplemented

    # variable to store last comment ID in for later
    comment_id_variable: Optional[str] = None

    # variable to store datetime of comment
    comment_datetime_variable: Optional[str] = None

    def execute(self) -> None:
        """ Post the issue to the fork """
        game = self.quest.quest_page.game
        game.load()
        fork_url = game.data.fork_url

        issue_id = getattr(self.quest.quest_data, self.issue_id_variable)

        logger.info("Creating comments", issue_id=issue_id, fork_url=fork_url)
        for character, body in self.character_comment_pairs:
            comment_id = character.issue_comment_create(fork_url, issue_id, body)

        if self.comment_id_variable:
            logger.info(
                "Storing comment Id in variable",
                comment_id=comment_id,
                variable=self.comment_id_variable,
            )
            setattr(self.quest.quest_data, self.comment_id_variable, comment_id)

        if self.comment_datetime_variable:
            setattr(
                self.quest.quest_data, self.comment_datetime_variable, datetime.now()
            )


class CheckIssueCommentReply(Stage):
    """ Check issues for reply """

    @property
    @abstractmethod
    def character(cls) -> Character:
        """ Which character will do the check and reply, character needs permission for the repo """
        return NotImplemented

    @property
    @abstractmethod
    def regex_pattern(cls) -> Pattern:
        """ Compiled regex pattern using re.compile() """
        return NotImplemented

    @property
    @abstractmethod
    def issue_id_variable(cls) -> int:
        """ Variable containing the ID of the issue to use """
        return NotImplemented

    # A list of possible responses
    incorrect_responses: List[str] = []

    # variable to store matching group values in
    result_groups_variable: Optional[str] = None

    # variable to store matching id in in
    result_id_variable: Optional[str] = None

    # variable to get check since from
    comment_datetime_variable: Optional[str] = None

    def fast_condition(self) -> bool:
        """If hasn't been run before, run once, otherwise fail to avoid hitting github API too much,
        letting notification scan process run this quest when it receives a notification"""

        if self.get_stage_data() is None:
            return self.condition()
        return False

    def condition(self) -> bool:
        """ Check messages """
        game = self.quest.quest_page.game
        game.load()
        fork_url = game.data.fork_url
        user = game.parent
        user.load()
        user_id = user.data.id

        issue_id = getattr(self.quest.quest_data, self.issue_id_variable)

        # use either last runtime (saved in stage data), or otherwise last comment datetime variable provided
        check_datetime = datetime.utcfromtimestamp(self.get_stage_data(0))
        if self.comment_datetime_variable is not None:
            check_datetime = max(
                check_datetime,
                getattr(self.quest.quest_data, self.comment_datetime_variable),
            )

        logger.info(
            "Fetching comments",
            user_id=user_id,
            issue_id=issue_id,
            fork_url=fork_url,
            check_datetime=check_datetime,
        )
        if check_datetime is None:
            comments = self.character.issue_comment_get_from_user(
                fork_url, issue_id, user_id
            )
        else:
            comments = self.character.issue_comment_get_from_user_since(
                fork_url, issue_id, user_id, check_datetime
            )
        logger.info("Got comments", count=len(comments))
        self.set_stage_data(datetime.now().timestamp())

        for comment_id, comment_body in comments.items():
            results = self.regex_pattern.match(comment_body)
            if results:

                logger.info("Got comment match on pattern!", comment_id=comment_id)
                if self.result_groups_variable:
                    setattr(
                        self.quest.quest_data,
                        self.result_groups_variable,
                        results.groups(),
                    )
                if self.result_id_variable:
                    setattr(self.quest.quest_data, self.result_id_variable, comment_id)
                return True

        # issue incorrect response
        if len(comments) and self.incorrect_responses:
            comment_id = self.character.issue_comment_create(
                fork_url, issue_id, random.choice(self.incorrect_responses)
            )

        return False
