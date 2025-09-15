import type { RegistryType } from "$lib/utils";
import type { DriftType } from "../monitoring/types";
import type { FeatureSchema } from "./datacard";

// Enums
export enum DataType {
  Pandas = "Pandas",
  Arrow = "Arrow",
  Polars = "Polars",
  Numpy = "Numpy",
  Image = "Image",
  Text = "Text",
  Dict = "Dict",
  Sql = "Sql",
  Profile = "Profile",
  TransformerBatch = "TransformerBatch",
  String = "String",
  TorchTensor = "TorchTensor",
  TorchDataset = "TorchDataset",
  TensorFlowTensor = "TensorFlowTensor",
  DMatrix = "DMatrix",
  Tuple = "Tuple",
  List = "List",
  Str = "Str",
  OrderedDict = "OrderedDict",
  Joblib = "Joblib",
  Base = "Base",
  Dataset = "Dataset",
  NotProvided = "NotProvided",
}

export enum ModelInterfaceType {
  Base = "Base",
  Sklearn = "Sklearn",
  CatBoost = "CatBoost",
  HuggingFace = "HuggingFace",
  LightGBM = "LightGBM",
  Lightning = "Lightning",
  Torch = "Torch",
  TensorFlow = "TensorFlow",
  VowpalWabbit = "VowpalWabbit",
  XGBoost = "XGBoost",
}

export enum ModelType {
  Transformers = "transformers",
  SklearnPipeline = "Pipeline",
  SklearnEstimator = "SklearnEstimator",
  StackingRegressor = "StackingRegressor",
  StackingClassifier = "StackingClassifier",
  StackingEstimator = "StackingEstimator",
  CalibratedClassifier = "CalibratedClassifierCV",
  LgbmRegressor = "LGBMRegressor",
  LgbmClassifier = "LGBMClassifier",
  XgbRegressor = "XGBRegressor",
  XgbClassifier = "XGBClassifier",
  XgbBooster = "Booster",
  LgbmBooster = "Booster",
  TensorFlow = "TensorFlow",
  TfKeras = "keras",
  Pytorch = "pytorch",
  PytorchLightning = "pytorch_lightning",
  Catboost = "CatBoost",
  Vowpal = "VowpalWabbit",
  Unknown = "Unknown",
}

export enum TaskType {
  Classification = "Classification",
  Regression = "Regression",
  Clustering = "Clustering",
  AnomalyDetection = "AnomalyDetection",
  TimeSeries = "TimeSeries",
  Forecasting = "Forecasting",
  Recommendation = "Recommendation",
  Ranking = "Ranking",
  Nlp = "Nlp",
  Image = "Image",
  Audio = "Audio",
  Video = "Video",
  Graph = "Graph",
  Tabular = "Tabular",
  TimeSeriesForecasting = "TimeSeriesForecasting",
  TimeSeriesAnomalyDetection = "TimeSeriesAnomalyDetection",
  TimeSeriesClassification = "TimeSeriesClassification",
  TimeSeriesRegression = "TimeSeriesRegression",
  TimeSeriesClustering = "TimeSeriesClustering",
  TimeSeriesRecommendation = "TimeSeriesRecommendation",
  TimeSeriesRanking = "TimeSeriesRanking",
  TimeSeriesNLP = "TimeSeriesNLP",
  TimeSeriesImage = "TimeSeriesImage",
  TimeSeriesAudio = "TimeSeriesAudio",
  TimeSeriesVideo = "TimeSeriesVideo",
  TimeSeriesGraph = "TimeSeriesGraph",
  TimeSeriesTabular = "TimeSeriesTabular",
  Optimization = "Optimization",
  Other = "Other",
}

// Processor types
export enum ProcessorType {
  Preprocessor = "preprocessor",
  Tokenizer = "tokenizer",
  FeatureExtractor = "feature_extractor",
  ImageProcessor = "image_processor",
}

// Interfaces

export interface OnnxSchema {
  input_features: FeatureSchema;
  output_features: FeatureSchema;
  onnx_version: string;
  feature_names: string[];
  onnx_type: string;
}

export interface OnnxSession {
  schema: OnnxSchema;
  session?: any; // Optional since it's Option<Py<PyAny>> in Rust
  quantized: boolean;
}

export interface DataProcessor {
  name: string;
  uri: string;
  type: ProcessorType;
}

export interface DriftProfileUri {
  root_dir: string;
  uri: string;
  drift_type: DriftType;
}

export interface ModelSaveKwargs {
  onnx?: Record<string, any>;
  model?: Record<string, any>;
  preprocessor?: Record<string, any>;
}

export interface ModelInterfaceSaveMetadata {
  model_uri: string;
  data_processor_map: Record<string, DataProcessor>;
  sample_data_uri?: string;
  onnx_model_uri?: string;
  drift_profile_uri_map?: Record<string, DriftProfileUri>;
  extra?: Record<string, any>;
  save_kwargs?: ModelSaveKwargs;
}

export interface ModelInterfaceMetadata {
  task_type: TaskType;
  model_type: ModelType;
  data_type: DataType;
  onnx_session?: OnnxSession;
  schema: FeatureSchema;
  save_metadata: ModelInterfaceSaveMetadata;
  extra_metadata: Record<string, string>;
  interface_type: ModelInterfaceType;
  model_specific_metadata: any;
}

export interface ModelCardMetadata {
  datacard_uid?: string;
  experimentcard_uid?: string;
  auditcard_uid?: string;
  interface_metadata: ModelInterfaceMetadata;
}

export interface ModelCard {
  name: string;
  space: string;
  version: string;
  uid: string;
  tags: string[];
  metadata: ModelCardMetadata;
  registry_type: RegistryType.Model;
  app_env: string;
  created_at: string; // ISO datetime string
  is_card: boolean;
  opsml_version: string;
}
