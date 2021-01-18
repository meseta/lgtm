""" Functions for generating database IDs """


def create_game_id(source: str, user_id: str) -> str:
    """ Create a user ID """
    if not source:
        raise ValueError("source can't be blank")
    if not user_id:
        raise ValueError("user_id can't be blank")
    return f"{source}:{user_id}"


def create_quest_id(game_id: str, quest_name: str) -> str:
    """ Create a quest name DB ID """
    if not game_id:
        raise ValueError("game_id can't be blank")
    if not quest_name:
        raise ValueError("quest_name can't be blank")
    return f"{game_id}:{quest_name}"
