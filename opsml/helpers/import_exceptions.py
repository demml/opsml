from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()


class OpsmlImportExceptions:
    @staticmethod
    def test_skl2onnx_imports():
        try:
            import skl2onnx
            import onnxmltools
        except ModuleNotFoundError as exec:
            logger.error(
                """Failed to import skl2onnx and onnxmltools. Please install skl2onnx and onnxmltools via opsml extras (opsml[skl2onnx])
                If you wish to convert your model to onnx"""
            )
            raise exec

    @staticmethod
    def test_tf2onnx_imports():
        try:
            import tf2onnx
        except ModuleNotFoundError as exec:
            logger.error(
                """Failed to import tf2onnx. Please install tf2onnx via opsml extras (opsml[tf2onnx])
                If you wish to convert your model to onnx"""
            )
            raise exec
