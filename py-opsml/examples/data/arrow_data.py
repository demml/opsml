import pyarrow as pa  # type: ignore
from opsml import ArrowData, CardRegistry, DataCard, RegistryType

registry = CardRegistry(RegistryType.Data)

n_legs = pa.array([2, 4, 5, 100])
animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
names = ["n_legs", "animals"]
table = pa.Table.from_arrays([n_legs, animals], names=names)

interface = ArrowData(data=table)
interface.create_data_profile()

card = DataCard(
    interface=interface,
    space="opsml",
    name="arrow_data",
)

registry.register_card(card=card)
registry.list_cards().as_table()
