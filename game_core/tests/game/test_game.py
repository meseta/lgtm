""" Tests for Game module """

import pytest
from game import Game


def test_parent(testing_game, testing_user):
    """ Test fetching parent object """
    assert testing_game.parent.key == testing_user.key


def test_game_repr(testing_game):
    """ Test repr """
    assert str(testing_game)
    assert repr(testing_game)


def test_second_creation(testing_game, random_id):
    """ Test second creation and setting fork_url """
    fork_url = "url_" + random_id

    game = Game(testing_game.key)
    assert game.exists
    assert testing_game.data.fork_url != fork_url

    game.set_fork_url(fork_url)
    game.save()

    testing_game.load()
    assert testing_game.data.fork_url == fork_url
