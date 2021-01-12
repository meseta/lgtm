""" Tests for main.py """

# pylint: disable=redefined-outer-name
def test_main(client):
    """ Placeholder """
    res = client.post("/")
    assert res.status_code == 200