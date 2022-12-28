from pydantic import BaseModel, Extra, root_validator
from typing import Optional, List, Dict, Any, Union
import pandas as pd
import numpy as np


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
    histogram: np.ndarray
    edges: np.ndarray

    class Config:
        arbitrary_types_allowed = True


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

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = True
        validate_assignment = False
