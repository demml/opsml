from pathlib import Path
from typing import Any, Dict, List, Optional

from ..types import DataType

class Distinct:
    @property
    def count(self) -> int:
        """total unique value counts"""

    @property
    def percent(self) -> float:
        """percent value uniqueness"""

class Quantiles:
    @property
    def q25(self) -> float:
        """25th quantile"""

    @property
    def q50(self) -> float:
        """50th quantile"""

    @property
    def q75(self) -> float:
        """75th quantile"""

    @property
    def q99(self) -> float:
        """99th quantile"""

class Histogram:
    @property
    def bins(self) -> List[float]:
        """Bin values"""

    @property
    def bin_counts(self) -> List[int]:
        """Bin counts"""

class NumericStats:
    @property
    def mean(self) -> float:
        """Return the mean."""

    @property
    def stddev(self) -> float:
        """Return the stddev."""

    @property
    def min(self) -> float:
        """Return the min."""

    @property
    def max(self) -> float:
        """Return the max."""

    @property
    def distinct(self) -> Distinct:
        """Distinct value counts"""

    @property
    def quantiles(self) -> Quantiles:
        """Value quantiles"""

    @property
    def histogram(self) -> Histogram:
        """Value histograms"""

class CharStats:
    @property
    def min_length(self) -> int:
        """Minimum string length"""

    @property
    def max_length(self) -> int:
        """Maximum string length"""

    @property
    def median_length(self) -> int:
        """Median string length"""

    @property
    def mean_length(self) -> float:
        """Mean string length"""

class WordStats:
    @property
    def words(self) -> Dict[str, Distinct]:
        """Distinct word counts"""

class StringStats:
    @property
    def distinct(self) -> Distinct:
        """Distinct value counts"""

    @property
    def char_stats(self) -> CharStats:
        """Character statistics"""

    @property
    def word_stats(self) -> WordStats:
        """word statistics"""

class FeatureProfile:
    @property
    def id(self) -> str:
        """Return the id."""

    @property
    def numeric_stats(self) -> Optional[NumericStats]:
        """Return the numeric stats."""

    @property
    def string_stats(self) -> Optional[StringStats]:
        """Return the string stats."""

    @property
    def timestamp(self) -> str:
        """Return the timestamp."""

    @property
    def correlations(self) -> Optional[Dict[str, float]]:
        """Feature correlation values"""

    def __str__(self) -> str:
        """Return the string representation of the feature profile."""

class DataProfile:
    """Data profile of features"""

    @property
    def features(self) -> Dict[str, FeatureProfile]:
        """Returns dictionary of features and their data profiles"""

    def __str__(self) -> str:
        """Return string representation of the data profile"""

    def model_dump_json(self) -> str:
        """Return json representation of data profile"""

    @staticmethod
    def model_validate_json(json_string: str) -> "DataProfile":
        """Load Data profile from json

        Args:
            json_string:
                JSON string representation of the data profile
        """

    def save_to_json(self, path: Optional[Path] = None) -> Path:
        """Save data profile to json file

        Args:
            path:
                Optional path to save the data profile. If None, outputs to `data_profile.json`

        Returns:
            Path to the saved data profile

        """

class DataProfiler:
    def __init__(self):
        """Instantiate DataProfiler class that is
        used to profile data"""

    def create_data_profile(
        self,
        data: Any,
        data_type: Optional[DataType] = None,
        bin_size: int = 20,
        compute_correlations: bool = False,
    ) -> None:
        """Create a data profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or pandas dataframe. Data is expected to not contain
                any missing values, NaNs or infinities. These values must be removed or imputed.
                If NaNs or infinities are present, the data profile will not be created.
            data_type:
                Optional data type. Inferred from data if not provided.
            bin_size:
                Optional bin size for histograms. Defaults to 20 bins.
            compute_correlations:
                Whether to compute correlations or not.

        Returns:
            DataProfile
        """
