from requests import Response
import math


def test_healthcheck(test_fastapi_client) -> None:
    response = test_fastapi_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"is_alive": True}


def test_healtherror(test_fastapi_client) -> None:
    response = test_fastapi_client.get("/healtherror")
    assert response.status_code == 500


def test_default_route(test_fastapi_client) -> None:
    response = test_fastapi_client.get("/")
    assert response.status_code == 404


def test_route_list(test_fastapi_client) -> None:
    response = test_fastapi_client.get("/route_list")
    assert response.status_code == 200


def test_tensorflow(test_fastapi_client, tensorflow_api_example):
    expected_value, example = tensorflow_api_example

    response: Response = test_fastapi_client.request(
        method="post",
        url=f"/predict/test-tensorflow/v1.0.0",
        json=example,
    )
    prediction = response.json()

    priority = prediction.get("priority")
    department = prediction.get("department")

    assert math.isclose(priority, expected_value["priority"], abs_tol=0.001)
    assert department is not None


def test_linear_reg(test_fastapi_client, linear_reg_api_example):
    expected_value, example = linear_reg_api_example

    response: Response = test_fastapi_client.request(
        method="post",
        url=f"/predict/test-lin-reg/v1.0.0",
        json=example,
    )
    prediction = response.json().get("variable")

    assert math.isclose(prediction, expected_value, abs_tol=0.001)


def test_sklearn_pipeline(test_fastapi_client, sklearn_pipeline_api_example):
    expected_value, example = sklearn_pipeline_api_example

    response: Response = test_fastapi_client.request(
        method="post",
        url=f"/predict/test-sklearn-pipeline/v1.0.0",
        json=example,
    )
    prediction = response.json().get("variable")

    assert math.isclose(prediction, expected_value, abs_tol=0.001)


def test_random_forest(test_fastapi_client, random_forest_api_example):
    expected_value, example = random_forest_api_example

    response: Response = test_fastapi_client.request(
        method="post",
        url=f"/predict/test-rand-forest/v1.0.0",
        json=example,
    )
    prediction = response.json().get("output_label")

    assert math.isclose(prediction, expected_value, abs_tol=0.001)
