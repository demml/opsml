from typing import Any, Dict, Optional
from opsml.registry.sql.records import LoadedDataRecord, LoadedModelRecord
from opsml.registry.storage.storage_system import StorageClientType


def test_data_metadata_backward():
    """
    This test is for ensuring introduction of metadata into
    datacards is backward compatible with V1 interface
    """

    class MockLoadedDataRecord(LoadedDataRecord):
        @classmethod
        def load_datacard_definition(
            cls, save_path: str, storage_client: Optional[StorageClientType] = None
        ) -> Dict[str, Any]:
            """Returned datacard for < v1.5"""
            return {
                "name": "name",
                "team": "team",
                "version": "version",
                "uid": "uid",
                "user_email": "user_email",
                "tags": {},
                "data_splits": [],
                "feature_map": {},
                "data_type": "dataframe",
                "dependent_vars": None,
                "feature_descriptions": {},
                "additional_info": {},
                "sql_logic": {},
                "runcard_uid": None,
                "pipelinecard_uid": None,
                "data_profile": None,
                "uris": {
                    "data_uri": "uri",
                    "datacard_uri": "uri",
                },
            }

    loaded_record = MockLoadedDataRecord(
        **{
            "storage_client": None,
            "datacard_uri": "uri",
        },
    )

    assert loaded_record.metadata.uris.data_uri == "uri"
    assert loaded_record.metadata.uris.datacard_uri == "uri"


def test_model_metadata_backward():
    """
    This test is for ensuring introduction of metadata into
    modelcards is backward compatible with V1 interface
    """

    class MockLoadedModelRecord(LoadedModelRecord):
        @classmethod
        def load_modelcard_definition(
            cls, values: Dict[str, Any], storage_client: Optional[StorageClientType] = None
        ) -> Dict[str, Any]:
            """Returned datacard for < v1.5"""

            return {
                "name": "name",
                "team": "team",
                "version": "version",
                "uid": "uid",
                "user_email": "user_email",
                "tags": {},
                "trained_model": None,
                "sample_input_data": None,
                "datacard_uid": "uid",
                "onnx_model_data": None,
                "onnx_model_def": None,
                "sample_data_type": None,
                "model_type": "model",
                "additional_onnx_args": None,
                "data_schema": None,
                "runcard_uid": None,
                "pipelinecard_uid": None,
                "to_onnx": False,
                "modelcard_uri": "uri",
                "trained_model_uri": "uri",
            }

    loaded_record = MockLoadedModelRecord(
        **{
            "storage_client": None,
            "modelcard_uri": "uri",
            "trained_model_uri": "uri",
        },
    )

    assert loaded_record.metadata.uris.modelcard_uri == "uri"
    assert loaded_record.metadata.uris.trained_model_uri == "uri"
