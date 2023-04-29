# import glob
# from typing import Any, Dict, List, Tuple, Type, cast
# import onnxruntime as rt
#
# from opsml.deploy.common import LoadedApiModelDef
#
## Models all share the same filename, but are stored in nested directories based on uid
# MODEL_SUFFIX = "model_def.json"
#
#
# class Model:
#    def __init__(self, model_path: str):
#        """Loads a ModelCard schema from JSON path
#        Args:
#            model_path (str): Path to JSON file
#        Returns:
#            Instantiated Onnx model to be used with API app
#        """
#        self.model = LoadedApiModelDef.parse_file(model_path)
#        self.name = self.model.model_name
#        self.version = self.model.model_version
#
#        self.sig_creator = ApiSigCreator(
#            expected_data_type=str(self.model.data_dict.get("data_type")),
#            model_type=self.model.model_type,
#            sample_data=self.model.sample_data,
#            input_features=cast(Dict[str, Any], self.model.input_signature.get("properties")),
#            output_features=cast(Dict[str, Any], self.model.output_signature.get("properties")),
#        )
#
#        self.sess: rt.InferenceSession = None
#        self._output_names = None
#        self.request_sig, self.response_sig = self.create_api_models()
#        self._confirm_model_loaded()
#
#    def _confirm_model_loaded(self):
#        logger.info("Model %s v%s successfully loaded", self.name, self.version)
#
#    def _create_request_model(self) -> Type[BaseModel]:
#        """Creates a request model to be used in Model predict route"""
#
#        input_title = f"{self.model.input_signature.get('title')}"
#        return self.sig_creator.create_model(
#            signature=self.sig_creator.input_features,
#            sig_model_name=f"{input_title}-{self.name}.v{self.version}",
#        )
#
#    def _create_response_model(self) -> Type[BaseModel]:
#        """Creates a response model to be used when returning model predictions"""
#
#        return self.sig_creator.create_model(
#            signature=self.sig_creator.output_features,
#            sig_model_name=f"Prediction-{self.name}.v{self.version}",
#        )
#
#    def create_api_models(self) -> Tuple[Type[BaseModel], Type[BaseModel]]:
#        request = self._create_request_model()
#        response = self._create_response_model()
#
#        return request, response
#
#    def start_onnx_session(self):
#        self.sess = cast(rt.InferenceSession, rt.InferenceSession(self.model.onnx_definition))
#        self._output_names = [output.name for output in self.sess.get_outputs()]
#
#    def _extract_predictions(self, prediction: List[Any]) -> Dict[str, List[Any]]:
#        """Parses onnx runtime prediction
#        Args:
#            Predictions (List): Onnx runtime prediction list
#        Returns:
#            Prediction in the form of a key value mapping
#        """
#        output_dict = {}
#        outputs = cast(List[str], self._output_names)
#        for idx, output in enumerate(outputs):
#            output_dict[output] = list(prediction[idx].flatten())
#        return output_dict
#
#    # def _get_defaults(self) -> Dict[str, Any]:
#    #    output_dict = {}
#    #    outputs = cast(List[str], self._output_names)
#    #    for _, output in enumerate(outputs):
#    #        output_dict[output] = [10]
#    #    return output_dict
#
#    def _predict_and_extract(self, payload: Base) -> Dict[str, List[Any]]:
#        """Creates prediction using onnx runtime
#        Args:
#            payload (Pydantic Base): Pydantic model containing features
#        Returns:
#            Prediction in the form ofa key value mapping
#        """
#
#        prediction = self.sess.run(
#            output_names=self._output_names,
#            input_feed=payload.to_onnx(),
#        )
#        return self._extract_predictions(prediction=prediction)
#
#    def predict(self, payload: Base) -> Dict[str, List[Any]]:
#
#        prediction = self._predict_and_extract(payload=payload)
#        return prediction
#
#
# class ModelLoader:
#    def __init__(self):
#        self.model_files = self._get_model_files()
#
#    def _get_model_files(self) -> List[str]:
#        """Load model file from environment"""
#
#        return list(set(glob.glob(f"**/**/{MODEL_SUFFIX}", recursive=True)))
#
#    def load_models(self) -> List[Model]:
#        """Load models"""
#        models = []
#        for model_path in self.model_files:
#            model = Model(model_path)
#            models.append(model)
#        return cast(List[Model], models)
#
