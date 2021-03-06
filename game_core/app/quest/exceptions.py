""" Exceptions used by this module """


class QuestError(Exception):
    """ General exception for quest errors """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class QuestLoadError(QuestError):
    """ Exception for when load fails """


class QuestSaveError(QuestError):
    """ Exception for when save fails """


class QuestDefinitionError(QuestError):
    """ Exception for when the quest definition is broken """
