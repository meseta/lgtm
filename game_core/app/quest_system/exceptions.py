""" Exceptions used by this module """


class QuestError(Exception):
    """ General exception for quest errors """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class QuestLoadError(QuestError):
    """ Exception for when load fails """
