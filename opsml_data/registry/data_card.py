from pydantic import BaseModel, root_validator, Extra, create_model
from typing import Optional, Union, Dict
from opsml_data.helpers.exceptions import NotOfCorrectType
from numpy.typing import NDArray
from pandas import DataFrame
from pyarrow import Table


class DataModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow


class DataCard(BaseModel):
    """Create a data card class from data.

    Args:
        data (np.ndarray, pd.DataFrame, pa.Table): Data to use for
        data card.
        data_name (str): What to name the data
        team (str): Team that this data is associated with
        user_email (str): Email to associate with data card
        data_splits (dictionary): Optional dictionary containing split. Defaults
        to None.
        logic for data. Splits can be defined in the following two ways:

        You can specify as many splits as you'd like

        (1) Split based on column value (works for pd.DataFrame)
            splits = {
                "train": {"col": "DF_COL", "val": 0}, -> "val" can also be a string
                "test": {"col": "DF_COL", "val": 1},
                "eval": {"col": "DF_COL", "val": 2},
                }

        (2) Index slicing (works for np.ndarray, pyarrow.Table, and pd.DataFrame)
            splits = {
                "train": {"start": 0, "stop": 10},
                "test": {"start": 11, "stop": 15},
                }

    Returns:
        Data card

    Examples:

    """

    data_name: Optional[str] = None
    team: str
    user_email: str
    data: Union[NDArray, DataFrame, Table]
    drift_report: Optional[DataFrame] = None
    data_splits: Optional[
        Dict[str : Dict[str : Union[str, int]]],
    ] = None

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow

    @root_validator(pre=True)
    def set_extras(cls, values):  # pylint: disable=no-self-argument
        """Pre checks"""

        # force strings to lower case
        for key, val in values.items():
            if isinstance(val, str):
                values[key] = val.lower()

        return values

    def split_data(self) -> DataModel:

        """Takes data from data card and splits it by the specified data splits

        Returns:
            DataModel (pydantic) with attributes corresponding to data splits

        """

        if self.data_splits is None:
            return DataModel(data=self.data)

        split_dict = {}
        if "col" in list(self.data_splits.values())[0].keys():

            if not isinstance(self.data, DataFrame):
                raise NotOfCorrectType(
                    """Data type must be of pandas dataframe when splitting with column conditions
                """
                )

            for split_name, split in self.data_splits.items():
                split_dict[split_name] = self.data.loc[self.data[split["col"] == split["val"]]]

        else:
            for split_name, split in self.data_splits.items():
                split_dict[split_name] = self.data[split_name["start"] : split_name["stop"] + 1]

        return DataModel.parse_obj(split_dict)

    # def calculate_drift(self):
    # pass

    # def register(self, data_name: str, drift: bool == False):
    #    """Registers the datacard from the current record"""


#
#    if drift:
#        if self.__getattribute__("drift_report") is None:
#            self.drift_report = self.calculate_drift()
#
#    meta: RegisterMetadata = DataRegistry().register_data(
#        data=self.data,
#        data_name=data_name,
#        drift_report=self.drift_report,
#        team=self.team,
#        user_email=self.user_email,
#    )

# for key, val in meta.dict().items():
# if self.__getattribute__(key) == None:
# self.__setattr__(key, val)
