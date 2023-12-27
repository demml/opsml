from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import pandas as pd
import polars as pl
from pydantic import BaseModel, ConfigDict, field_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.profile.profile_data import DataProfiler, ProfileReport
from opsml.registry.data.splitter import DataHolder, DataSplit, DataSplitter
from opsml.registry.types import Suffix, Feature

logger = ArtifactLogger.get_logger()


class DataInterface(BaseModel):
    """Base data interface for all data types"""

    data: Optional[Any] = None
    data_splits: List[DataSplit] = []
    dependent_vars: List[Union[int, str]] = []
    data_profile: Optional[ProfileReport] = None
    feature_map: Dict[str, Feature] = {}

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
    )

    @property
    def data_type(self) -> str:
        raise NotImplementedError

    @field_validator("data_profile", mode="before")
    @classmethod
    def _check_profile(cls, profile: Optional[ProfileReport]) -> Optional[ProfileReport]:
        if profile is not None:
            from ydata_profiling import ProfileReport as ydata_profile

            assert isinstance(profile, ydata_profile)
        return profile

    def save_data(self, path: Path) -> Path:
        """Saves data to path. Base implementation use Joblib

        Args:
            path:
                Pathlib object
        """
        assert self.data is not None, "No data detected in interface"
        save_path = path.with_suffix(Suffix.JOBLIB.value)
        joblib.dump(self.data, save_path)

        return save_path

    def load_data(self, path: Path) -> Path:
        """Load data from pathlib object

        Args:
            path:
                Pathlib object
        """

        save_path = path.with_suffix(Suffix.JOBLIB.value)
        self.data = joblib.load(save_path)

    def load_profile(self, path: Path) -> Path:
        """Load data profile from pathlib object

        Args:
            path:
                Pathlib object
        """

        save_path = path.with_suffix(Suffix.JOBLIB.value)
        self.data_profile = joblib.load(save_path)

    def save_data_profile(self, path: Path, save_type: str) -> Path:
        """Saves data profile to path. Data profiles are saved as joblib
        joblib

        Args:
            path:
                Pathlib object
        """
        assert self.data_profile is not None, "No data profile detected in interface"

        if save_type == "html":
            profile_artifact = self.data_profile.to_html()
            save_path = path.with_suffix(Suffix.HTML.value)
            save_path.write_text(profile_artifact, encoding="utf-8")
        else:
            profile_artifact = self.data_profile.dumps()
            save_path = path.with_suffix(Suffix.JOBLIB.value)
            joblib.dump(profile_artifact, save_path)

        return save_path

    def create_data_profile(self, sample_perc: float = 1) -> ProfileReport:
        """Creates a data profile report

        Args:
            sample_perc:
                Percentage of data to use when creating a profile. Sampling is recommended for large dataframes.
                Percentage is expressed as a decimal (e.g. 1 = 100%, 0.5 = 50%, etc.)

        """

        if isinstance(self.data, (pl.DataFrame, pd.DataFrame)):
            if self.data_profile is None:
                self.data_profile = DataProfiler.create_profile_report(
                    data=self.data,
                    name=self.name,
                    sample_perc=min(sample_perc, 1),  # max of 1
                )
                return self.data_profile

            logger.info("Data profile already exists")
            return self.data_profile

        raise ValueError("A pandas dataframe type is required to create a data profile")

    def split_data(self) -> DataHolder:
        """
        Loops through data splits and splits data either by indexing or
        column values

        Example:

            ```python
            card_info = CardInfo(name="linnerrud", team="tutorial", user_email="user@email.com")
            data_card = DataCard(
                info=card_info,
                data=data,
                dependent_vars=["Pulse"],
                # define splits
                data_splits=[
                    {"label": "train", "indices": train_idx},
                    {"label": "test", "indices": test_idx},
                ],

            )

            splits = data_card.split_data()
            print(splits.train.X.head())

               Chins  Situps  Jumps
            0    5.0   162.0   60.0
            1    2.0   110.0   60.0
            2   12.0   101.0  101.0
            3   12.0   105.0   37.0
            4   13.0   155.0   58.0
            ```

        Returns
            Class containing data splits
        """
        if self.data is None:
            raise ValueError("Data must not be None. Either supply data or load data")

        if len(self.data_splits) > 0:
            data_holder = DataHolder()
            for data_split in self.data_splits:
                label, data = DataSplitter.split(
                    split=data_split,
                    dependent_vars=self.dependent_vars,
                    data=self.data,
                    data_type=self.data_type,
                )
                setattr(data_holder, label, data)

            return data_holder
        raise ValueError("No data splits provided")
