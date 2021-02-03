""" Base Classes for quest objects """
from __future__ import annotations

from typing import List, Dict, ClassVar, Type, cast, TYPE_CHECKING

from abc import ABC, abstractmethod
from inspect import isclass
from graphlib import TopologicalSorter, CycleError
from datetime import datetime

from structlog import get_logger
from pydantic import ValidationError
from semver import VersionInfo  # type:  ignore

from tick import TickType
from .exceptions import QuestError, QuestLoadError, QuestDefinitionError
from .models import Difficulty, QuestBaseModel


if TYPE_CHECKING:
    from quest_page import QuestPage  # pragma: no cover
    from .stage import Stage  # pragma: no cover

logger = get_logger(__name__)


def semver_safe(start: VersionInfo, dest: VersionInfo) -> bool:
    """ whether semver loading is going to be safe """
    if start.major != dest.major:
        return False

    # check it's not a downgrade of minor version
    if start.minor > dest.minor:
        return False

    return True


class Quest(ABC):
    @classmethod
    def from_name(cls, name: str, quest_page: QuestPage) -> Quest:
        from .loader import all_quests  # avoid cyclic import

        try:
            quest_class = all_quests[name]
        except KeyError as err:
            raise QuestError(f"No quest name {name}") from err

        return quest_class(quest_page)

    @property
    @abstractmethod
    def version(cls) -> VersionInfo:
        """ The version of this quest, used to check against load data """
        return NotImplemented

    @property
    @abstractmethod
    def difficulty(cls) -> Difficulty:
        """ Difficulty metadata, for display purposes only """
        return NotImplemented

    @property
    @abstractmethod
    def description(cls) -> str:
        """ Quest description metadata, for display purposes only """
        return NotImplemented

    @property
    @abstractmethod
    def stages(cls) -> Dict[str, Type[Stage]]:
        """ The initial default data to start quests with """
        return NotImplemented

    # default, overridable model is empty pydantic model
    QuestDataModel: ClassVar[Type[QuestBaseModel]] = QuestBaseModel

    def __init_subclass__(cls):
        """ Subclasses instantiate by copying default data """
        from .stage import Stage  # avoid cyclic import

        # build class list
        cls.stages = {}
        for name, class_var in vars(cls).items():
            if isclass(class_var) and issubclass(class_var, Stage):
                cls.stages[name] = class_var

    # loaded player quest data
    quest_data: QuestBaseModel
    graph: TopologicalSorter

    # the parent object
    quest_page: QuestPage

    def __init__(self, quest_page):
        self.quest_page = quest_page
        self.quest_data = self.QuestDataModel()

    def load_stages(self) -> None:
        """ loads the stages """

        # load graph
        self.graph = TopologicalSorter()
        for stage_name, StageClass in self.stages.items():
            for child_name in cast(List[str], StageClass.children):
                if child_name not in self.stages:
                    raise QuestDefinitionError(
                        f"{self} does not have stage named '{child_name}'"
                    )
                self.graph.add(child_name, stage_name)

        try:
            self.graph.prepare()
        except CycleError as err:
            raise QuestDefinitionError(f"{self} prepare failed! {err}") from err

    def load_raw(self, version_str: str, serialized_data: str) -> None:
        """ Load save data back into structure """

        # check save version is safe before upgrading
        try:
            save_semver = VersionInfo.parse(version_str)
        except ValueError as err:
            raise QuestLoadError(f"Invalid version string {version_str}") from err

        if not semver_safe(save_semver, self.version):
            raise QuestLoadError(
                f"{self} Unsafe version mismatch in! {save_semver} -> {self.version}"
            )

        try:
            self.quest_data = self.QuestDataModel.parse_raw(serialized_data)
        except ValidationError as err:
            raise QuestLoadError(f"{self} data validation error! {err}") from err

    def save_raw(self) -> str:
        """ Returns serialized data to save """
        return self.quest_data.json()

    def execute(self, tick_type: TickType = TickType.FULL) -> None:
        """ Executes stages, tick_type helps nodes know whether to skip certain stages """

        log = logger.bind(quest=self)
        log.info("Begin execution")

        self.load_stages()
        while self.graph.is_active():
            ready_nodes = self.graph.get_ready()

            if not ready_nodes:
                log.info("No more ready nodes, stopping execution")
                break

            log.info("Got Ready nodes", ready_nodes=ready_nodes)

            for node in ready_nodes:
                # skip if completed, avoids triggering two final stages
                if self.quest_page.is_quest_complete():
                    log.info("Done flag set, skipping the rest")
                    return

                # completed node: TODO: just not put completed nodes into the graph?
                if self.quest_page.is_stage_complete(node):
                    self.graph.done(node)
                    log.info(
                        "Node is already complete, skipping",
                        node=node,
                    )
                    continue

                log_node = log.bind(node=node)
                log_node.info("Begin processing stage")

                # instantiate stage and execute
                StageClass = self.stages[node]
                stage = StageClass(self)
                stage.prepare()

                if tick_type == TickType.FAST:
                    condition = stage.fast_condition
                    execute = stage.fast_execute
                else:
                    condition = stage.condition
                    execute = stage.execute

                if condition():
                    log_node.info("Condition check passed, executing")
                    execute()

                    if stage.is_done():
                        log_node.info("Stage reports done")
                        self.quest_page.mark_stage_complete(node)
                        self.graph.done(node)

                    self.quest_data.last_run = datetime.now()

        log.info("Done processing node")

    def __repr__(self):
        return f"{self.__class__.__name__}(quest_page={self.quest_page})"
