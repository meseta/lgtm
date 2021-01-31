""" Tests for main.py """

from models import StatusReturn

# pylint: disable=redefined-outer-name
def test_success():
    """ Test success return model """

    retval = StatusReturn(success=True)
    assert retval.http_code == 200


def test_error():
    """ Test error """

    retval = StatusReturn(error="ouchie")
    assert retval.http_code == 400


def test_http_code_override():
    """ Test when http code is explicit """

    retval = StatusReturn(success=True, http_code=666)
    assert retval.http_code == 666

    retval = StatusReturn(error="ouchie", http_code=999)
    assert retval.http_code == 999

    retval = StatusReturn(success=True, error="ouchie", http_code=888)
    assert retval.http_code == 888
