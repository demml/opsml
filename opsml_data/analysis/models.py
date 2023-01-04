from pydantic import BaseModel
from typing import Optional, Any, List
import pandas as pd
from enum import Enum


class PayAnalysisData(BaseModel):
    ids: List[str]
    checkout_predictions: Optional[List[float]] = None
    delivery_predictions: Optional[List[float]] = None
    pick_predictions: Optional[List[float]] = None
    drop_predictions: Optional[List[float]] = None
    drive_predictions: Optional[List[float]] = None
    wait_predictions: Optional[List[float]] = None

    class Config:
        arbitrary_types_allowed = True


class AnalysisAttributes(BaseModel):
    id_col: str
    compute_env: str
    analysis_level: str
    analysis_type: str
    table_name: str
    metro_level: bool
    outlier_removal: bool


class PayDataFrame(pd.DataFrame):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """instantiate as normal, then validate using pydantic"""
        super().__init__(*args, **kwargs)
        self.columns = map(str.lower, self.columns)

    def get_valid_data(self) -> PayAnalysisData:
        return PayAnalysisData(**self.to_dict(orient="list"))
