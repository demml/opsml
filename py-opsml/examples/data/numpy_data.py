import numpy as np
from opsml import CardRegistry, DataCard, RegistryType
from opsml.data import DataSplit, DataSplits, DependentVars, NumpyData, StartStopSplit

"""This example demonstrates how to save a numpy array to a NumpyData interface with data splits
"""

registry = CardRegistry(RegistryType.Data)

array = np.random.rand(1000, 100)

train_split = DataSplit(
    label="train",
    start_stop_split=StartStopSplit(
        start=0,
        stop=800,
    ),
)

test_split = DataSplit(
    label="test",
    start_stop_split=StartStopSplit(
        start=800,
        stop=1000,
    ),
)

splits = DataSplits(
    [train_split, test_split],
)
dependent_vars = DependentVars(column_indices=[99])

interface = NumpyData(
    data=array,
    data_splits=splits,
    dependent_vars=dependent_vars,
)

datasets = interface.split_data()

print("Shape of train data: ", (datasets["train"].x.shape, datasets["train"].y.shape))
print("Shape of test data: ", (datasets["test"].x.shape, datasets["test"].y.shape))

card = DataCard(
    interface=interface,
    space="opsml",
    name="numpy_data",
)

registry.register_card(card=card)


registry.list_cards().as_table()
