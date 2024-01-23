from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import pandas as pd
import polars as pl
from pydantic import BaseModel, ConfigDict, field_validator

from opsml.data.splitter import Data, DataSplit, DataSplitter
from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import FileUtils
from opsml.types import CommonKwargs, Feature, Suffix

logger = ArtifactLogger.get_logger()

try:
    from ydata_profiling import ProfileReport
except ModuleNotFoundError:
    ProfileReport = Any


class DataInterface(BaseModel):
    """Base data interface for all data types

    Args:
        data:
            Data. Can be a pyarrow table, pandas dataframe, polars dataframe
            or numpy array
        dependent_vars:
            List of dependent variables. Can be string or index if using numpy
        data_splits:
            Optional list of `DataSplit`
        data_profile:
            Optional ydata-profiling `ProfileReport`
        feature_map:
            Dictionary of features -> automatically generated
        feature_descriptions:
            Dictionary or feature descriptions
        sql_logic:
            Sql logic used to generate data

    """

    data: Optional[Any] = None
    data_splits: List[DataSplit] = []
    dependent_vars: List[Union[int, str]] = []
    data_profile: Optional[ProfileReport] = None
    feature_map: Dict[str, Feature] = {}
    feature_descriptions: Dict[str, str] = {}
    sql_logic: Dict[str, str] = {}

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
    )

    @property
    def data_type(self) -> str:
        return CommonKwargs.UNDEFINED.value

    @field_validator("sql_logic", mode="before")
    @classmethod
    def _load_sql(cls, sql_logic: Dict[str, str]) -> Dict[str, str]:
        if not bool(sql_logic):
            return sql_logic

        for name, query in sql_logic.items():
            if ".sql" in query:
                try:
                    sql_path = FileUtils.find_filepath(name=query)
                    with open(sql_path, "r", encoding="utf-8") as file_:
                        query_ = file_.read()
                    sql_logic[name] = query_

                except Exception as error:
                    raise ValueError(f"Could not load sql file {query}. {error}") from error

        return sql_logic

    def add_sql(
        self,
        name: str,
        query: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        """
        Adds a query or query from file to the sql_logic dictionary. Either a query or
        a filename pointing to a sql file are required in addition to a name.

        Args:
            name:
                Name for sql query
            query:
                SQL query
            filename: Filename of sql query
        """
        if query is not None:
            self.sql_logic[name] = query

        elif filename is not None:
            sql_path = str(FileUtils.find_filepath(name=filename))
            with open(sql_path, "r", encoding="utf-8") as file_:
                query = file_.read()
            self.sql_logic[name] = query

        else:
            raise ValueError("SQL Query or Filename must be provided")

    @field_validator("data_profile", mode="before")
    @classmethod
    def _check_profile(cls, profile: Optional[ProfileReport]) -> Optional[ProfileReport]:
        if profile is not None:
            from ydata_profiling import ProfileReport as ydata_profile

            assert isinstance(profile, ydata_profile)
        return profile

    def save_data(self, path: Path) -> None:
        """Saves data to path. Base implementation use Joblib

        Args:
            path:
                Pathlib object
        """
        assert self.data is not None, "No data detected in interface"
        joblib.dump(self.data, path)

        self.feature_map = {
            "features": Feature(
                feature_type=str(type(self.data)),
                shape=CommonKwargs.UNDEFINED.value,
            )
        }

    def load_data(self, path: Path) -> None:
        """Load data from pathlib object

        Args:
            path:
                Pathlib object
        """

        self.data = joblib.load(path)

    def load_data_profile(self, path: Path) -> None:
        """Load data profile from pathlib object

        Args:
            path:
                Pathlib object
        """
        self.data_profile = ProfileReport().loads(
            joblib.load(path),
        )

    def save_data_profile(self, path: Path) -> None:
        """Saves data profile to path. Data profiles are saved as joblib
        joblib

        Args:
            path:
                Pathlib object
        """
        assert self.data_profile is not None, "No data profile detected in interface"

        if path.suffix == Suffix.HTML.value:
            profile_artifact = self.data_profile.to_html()
            path.write_text(profile_artifact, encoding="utf-8")
        else:
            profile_artifact = self.data_profile.dumps()
            joblib.dump(profile_artifact, path)

    def create_data_profile(self, sample_perc: float = 1, name: str = "data_profile") -> ProfileReport:
        """Creates a data profile report

        Args:
            sample_perc:
                Percentage of data to use when creating a profile. Sampling is recommended for large dataframes.
                Percentage is expressed as a decimal (e.g. 1 = 100%, 0.5 = 50%, etc.)
            name:
                Name of data profile

        """
        from opsml.profile.profile_data import DataProfiler

        if isinstance(self.data, (pl.DataFrame, pd.DataFrame)):
            if self.data_profile is None:
                self.data_profile = DataProfiler.create_profile_report(
                    data=self.data,
                    name=name,
                    sample_perc=min(sample_perc, 1),  # max of 1
                )
                return self.data_profile

            logger.info("Data profile already exists")
            return self.data_profile

        raise ValueError("A pandas dataframe type is required to create a data profile")

    def split_data(self) -> Dict[str, Data]:
        """
        Loops through data splits and splits data either by indexing or
        column values

        Example:

            ```python
            card_info = CardInfo(name="linnerrud", repository="tutorial", contact="user@email.com")
            data_card = DataCard(
                info=card_info,
                data=data,
                dependent_vars=["Pulse"],
                # define splits
                data_splits=[
                    DataSplit(label="train", indices=train_idx),
                    DataSplit(label="test", indices=test_idx),
                ],

            )

            splits = data_card.split_data()
            print(splits["train"].X.head())

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
            data_holder: Dict[str, Data] = {}
            for data_split in self.data_splits:
                label, data = DataSplitter.split(
                    split=data_split,
                    dependent_vars=self.dependent_vars,
                    data=self.data,
                    data_type=self.data_type,
                )
                data_holder[label] = data

            return data_holder
        raise ValueError("No data splits provided")

    @property
    def data_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.JOBLIB.value

    @staticmethod
    def name() -> str:
        raise NotImplementedError
