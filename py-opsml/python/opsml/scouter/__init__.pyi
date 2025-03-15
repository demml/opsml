# type: ignore
# pylint: disable=relative-beyond-top-level

from typing import Any, List, Optional, Union, overload

from ..scouter.drift import (
    CustomDriftProfile,
    CustomMetric,
    CustomMetricDriftConfig,
    PsiDriftConfig,
    PsiDriftProfile,
    SpcDriftConfig,
    SpcDriftProfile,
)
from ..scouter.types import DataType

class Drifter:
    def __init__(self) -> None:
        """Instantiate Rust Drifter class that is
        used to create monitoring profiles and compute drifts.
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: SpcDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile:
        """Create a SPC (Statistical process control) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            config:
                SpcDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile:
        """Create a SPC (Statistical process control) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            config:
                SpcDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: PsiDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> PsiDriftProfile:
        """Create a PSI (population stability index) drift profile from the provided data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe or a pandas dataframe.
            config:
                PsiDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            PsiDriftProfile
        """

    @overload
    def create_drift_profile(
        self,
        data: Union[CustomMetric, List[CustomMetric]],
        config: CustomMetricDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> CustomDriftProfile:
        """Create a custom drift profile from data.

        Args:
            data:
                CustomMetric or list of CustomMetric.
            config:
                CustomMetricDriftConfig
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            CustomDriftProfile
        """

    def create_drift_profile(  # type: ignore
        self,
        data: Any,
        config: Optional[Union[SpcDriftConfig, PsiDriftConfig, CustomMetricDriftConfig]] = None,
        data_type: Optional[DataType] = None,
    ) -> Union[SpcDriftProfile, PsiDriftProfile, CustomDriftProfile]:
        """Create a drift profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe, pandas dataframe or a list of CustomMetric if creating
                a custom metric profile.
            config:
                Drift config that will be used for monitoring
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    def compute_drift(
        self,
        data: Any,
        drift_profile: Union[SpcDriftProfile, PsiDriftProfile],
        data_type: Optional[DataType] = None,
    ) -> Any:
        """Create a drift profile from data.

        Args:
            data:
                Data to create a data profile from. Data can be a numpy array,
                a polars dataframe, pandas dataframe or a list of CustomMetric if creating
                a custom metric profile.
            drift_profile:
                Drift profile to use to compute drift map
            data_type:
                Optional data type. Inferred from data if not provided.

        Returns:
            SpcDriftMap or PsiDriftMap
        """

class DataProfiler:
    def __init__(self):
        """Instantiate Rust TestProfiler class that is
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
