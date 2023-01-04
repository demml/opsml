from enum import Enum
from typing import List, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel, Extra, root_validator


class DriftData(BaseModel):
    X: pd.DataFrame
    y: np.ndarray
    target: Optional[np.ndarray] = None

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True
        allow_mutation = True
        validate_assignment = False


class ExtractedAttributes(BaseModel):
    reference_data: np.ndarray
    current_data: np.ndarray
    feature_type: int
    target_val: int

    class Config:
        arbitrary_types_allowed = True


class FeatureImportance(BaseModel):
    importance: Optional[float] = None
    auc: float


class HistogramOutput(BaseModel):
    values: np.ndarray
    bins: np.ndarray

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def modify_attr(cls, values):  # pylint: disable=no-self-argument
        bins = values["bins"]
        vals = values["values"]

        values["bins"] = bins[: len(vals)]

        return values


class FeatureStatsOutput(BaseModel):
    historgram: HistogramOutput
    missing_records: str
    unique: int
    type_: str
    target_feature: int


class DriftReport(BaseModel):
    intersection: float
    missing_records: str
    unique: int
    reference_distribution: HistogramOutput
    current_distribution: HistogramOutput
    target_feature: int
    feature_importance: Optional[float] = None
    feature_auc: Optional[float] = None
    feature_type: int

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = True
        validate_assignment = False


class ParsedFeatures(BaseModel):
    feature: List[Optional[str]] = []
    values: List[Optional[float]] = []
    bins: List[Optional[float]] = []
    label: List[Optional[str]] = []
    feature_type: List[Optional[int]] = []


class ParsedFeatureImportance(BaseModel):
    feature: List[str] = []
    auc: List[Optional[float]] = []
    importance: List[Optional[float]] = []


class ParsedFeatureDataFrames(BaseModel):
    distribution_dataframe: pd.DataFrame
    importance_dataframe: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True


class FeatureTypes(Enum):
    CATEGORICAL = 0
    NUMERIC = 1


class ChartType(Enum):
    CATEGORICAL = 0
    NUMERIC = 1
    AUC = 2
