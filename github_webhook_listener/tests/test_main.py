from functions_framework import create_app  # type: ignore


def test_hello_world(source, random_id):
    client = create_app("hello_world", source).test_client()

    res = client.post("/", json=dict(name=random_id))
    assert res.status_code == 200
    assert res.get_data(as_text=True) == f"Hello {random_id}!"
