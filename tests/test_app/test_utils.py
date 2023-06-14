from opsml.app.routes.utils import replace_proxy_root


def test_replace_proxy():
    fake_url = "mlflow-artifacts:/1/blah/"
    storage_root = "gs://bucket"
    proxy_root = "mlflow-artifacts:/"

    record = {"name": "test", "modelcard_uri": fake_url}
    new_record = replace_proxy_root(card=record, storage_root=storage_root, proxy_root=proxy_root)

    assert storage_root in new_record["modelcard_uri"]
    assert proxy_root not in new_record["modelcard_uri"]
