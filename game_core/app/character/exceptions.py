""" Exceptions used by this module """


class CharacterError(Exception):
    """ General exception for characters """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
