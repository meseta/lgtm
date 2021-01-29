""" Tests for Game module """

import pytest
from app.firebase_utils import db
from app.game import Game, NoGame, find_game_by_user
from app.user import NoUser

# pylint: disable=redefined-outer-name
def test_bad_new(random_user):
    """ Errors caused by invaild new arguments """

    game = Game("")
    with pytest.raises(Exception):
        game.new("abc")

    game = Game(random_user)
    with pytest.raises(Exception):
        game.new("")


def test_nouser_init():
    """ Test invalid initialization with bad user """
    game = Game(NoUser)
    with pytest.raises(Exception):
        game.key


def test_game_repr(random_user):
    game = Game(random_user)

    assert str(game)
    assert repr(game)


def test_second_creation(testing_game, random_id):
    """ Test second creation of game """
    fork_url = "url_" + random_id

    # assert url isn't what we'll set it to
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("fork_url") != fork_url

    # make new game, this will update fork_url
    game = Game(testing_game.user)
    game.new(fork_url)

    # check it
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("fork_url") == fork_url


def test_fail_find_user(random_user):
    """ Test failing to finding a game by user """

    game = find_game_by_user(random_user)
    assert game is NoGame


def test_find_user(testing_game):
    """ Test finding a game by user """

    user = testing_game.user

    game = find_game_by_user(user)
    assert game.key == testing_game.key


def test_assign_uid(testing_game, random_id):
    """ Test assigning game to an UID """

    new_uid = "uid_" + random_id

    # assert uid isn't what we'll set it to
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("user_uid") != new_uid

    testing_game.assign_to_uid(new_uid)

    # check it
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("user_uid") == new_uid
