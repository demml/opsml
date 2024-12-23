from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib  # type: ignore
from opsml import DataType, Feature, FileUtils, OpsmlLogger
from opsml.interfaces.data.features import Data, DataProfiler, DataSplit, DataSplitter
from pydantic import BaseModel, ConfigDict, field_validator
from scouter import DataProfile

logger = OpsmlLogger.get_logger()


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
    data_profile: Optional[DataProfile] = None
    feature_map: Dict[str, Feature] = {}
    feature_descriptions: Dict[str, str] = {}
    sql_logic: Dict[str, str] = {}
    has_profile: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
    )

    @property
    def data_type(self) -> DataType:
        return DataType.Base

    @field_validator("sql_logic", mode="before")
    @classmethod
    def _load_sql(cls, sql_logic: Dict[str, str]) -> Dict[str, str]:
        if not bool(sql_logic):
            return sql_logic

        for name, query in sql_logic.items():
            if ".sql" in query:
                try:
                    sql_logic[name] = FileUtils.open_file(query)

                except Exception as error:
                    raise ValueError(
                        f"Could not load sql file {query}. {error}"
                    ) from error

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
            self.sql_logic[name] = FileUtils.open_file(filename)

        else:
            raise ValueError("SQL Query or Filename must be provided")

    @field_validator("data_profile", mode="before")
    @classmethod
    def _check_profile(cls, profile: Optional[DataProfile]) -> Optional[DataProfile]:
        if profile is not None:
            assert isinstance(profile, DataProfile)
            cls.has_profile = True
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
                shape=[],
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

        profile = DataProfile.model_validate_json(path.read_text(encoding="utf-8"))
        self.data_profile = profile

    def save_data_profile(self, path: Path) -> None:
        """Saves data profile to path. Data profiles are saved as json object.

        Args:
            path:
                Pathlib path
        """
        assert self.data_profile is not None, "No data profile detected in interface"
        self.data_profile.save_to_json(path)

    def create_data_profile(
        self, bin_size: int = 20, compute_correlations: bool = False
    ) -> DataProfile:
        """Creates a data profile report

        Args:
            bin_size:
                number of bins for histograms. Default is 20
            compute_correlations:
                whether to compute correlations. Default is False

        """
        profiler = DataProfiler()

        if self.data_profile is None:
            self.data_profile = profiler.create_profile_report(
                self.data,  # type: ignore
                bin_size,
                compute_correlations,
            )
            self.has_profile = True
            return self.data_profile

        logger.info("Data profile already exists")
        return self.data_profile

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

    @staticmethod
    def is_data_interface() -> bool:
        raise NotImplementedError
