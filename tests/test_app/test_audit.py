from typing import Tuple

from starlette.testclient import TestClient

from opsml.app.routes.pydantic_models import AuditFormRequest
from opsml.cards import AuditCard, DataCard, ModelCard


##### Test audit
def test_audit(test_app: TestClient, populate_model_data_for_route: Tuple[ModelCard, DataCard, AuditCard]) -> None:

    modelcard, datacard, auditcard = populate_model_data_for_route

    response = test_app.get("/opsml/audit/")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/audit/?repository={modelcard.repository}")
    assert response.status_code == 200

    response = test_app.get(f"/opsml/audit/?repository={modelcard.repository}&?model={modelcard.name}")
    assert response.status_code == 200

    audit_form = AuditFormRequest(
        selected_model_name=modelcard.name,
        selected_model_repository=modelcard.repository,
        selected_model_version=modelcard.version,
        selected_model_contact=modelcard.contact,
        name="model_audit",
        repository="mlops",
        contact="mlops.com",
    )

    response = test_app.post(
        "/opsml/audit/save",
        data=audit_form.model_dump(),
    )

    assert response.status_code == 200

    response = test_app.get(
        f"/opsml/audit/?repository={modelcard.repository}&model={modelcard.name}&version={modelcard.version}"
    )
    assert response.status_code == 200

    # upload
    # without uid
    file_ = "tests/assets/audit_file.csv"
    response = test_app.post(
        "/opsml/audit/upload",
        data=audit_form.model_dump(),
        files={"audit_file": open(file_, "rb")},
    )
    assert response.status_code == 200

    # with uid
    audit_form = AuditFormRequest(
        selected_model_name=modelcard.name,
        selected_model_repository=modelcard.repository,
        selected_model_version=modelcard.version,
        selected_model_contact=modelcard.contact,
        name="model_audit",
        repository="mlops",
        contact="mlops.com",
        uid=auditcard.uid,
    )

    response = test_app.post(
        "/opsml/audit/upload",
        data=audit_form.model_dump(),
        files={"audit_file": open(file_, "rb")},
    )
    assert response.status_code == 200

    # test downloading audit file
    response = test_app.post(
        "/opsml/audit/download",
        data=audit_form.model_dump(),
    )
    assert response.status_code == 200
