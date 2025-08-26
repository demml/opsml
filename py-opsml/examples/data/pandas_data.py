from opsml import CardRegistry, DataCard, RegistryType
from opsml.data import ColumnSplit, DataSplit, DataSplits, DependentVars, PandasData
from opsml.helpers.data import create_fake_data

"""This example demonstrates how to save a pandas dataframe to a PandasData interface with data splits
"""

registry = CardRegistry(RegistryType.Data)


data, _ = create_fake_data(n_samples=1200, n_categorical_features=2)


train_split = DataSplit(
    label="train",
    column_split=ColumnSplit(column_name="col_0", column_value=0.7, inequality="<="),
)

test_split = DataSplit(
    label="test",
    column_split=ColumnSplit(column_name="col_0", column_value=0.7, inequality=">"),
)
splits = DataSplits(
    [train_split, test_split],
)
dependent_vars = DependentVars(column_names=["col_1"])

interface = PandasData(
    data=data,
    data_splits=splits,
    dependent_vars=dependent_vars,
)

# create data profile
interface.create_data_profile()

datasets = interface.split_data()

print("Shape of train data: ", (datasets["train"].x.shape, datasets["train"].y.shape))
print("Shape of test data: ", (datasets["test"].x.shape, datasets["test"].y.shape))

card = DataCard(
    interface=interface,
    space="opsml",
    name="pandas_data",
)

registry.register_card(card=card)


registry.list_cards().as_table()

print(card.interface.schema)
