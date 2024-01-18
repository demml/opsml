# PandasData

The `PandasData` interface is used to store data from a `pandas` dataframe. It is a subclass of the `DataInterface` and inherits all of its methods and properties.



## Example

```python
from opsml import PandasData, CardInfo, DataCard, CardRegistry

info = CardInfo(name="linear-regression", team="opsml", contact="user@email.com")
data_registry = CardRegistry("data")

# create fake data
X, _ = create_fake_data(n_samples=1000, task_type="regression")

# Create data interface
data_interface = PandasData(data=X)

# Create and register datacard
datacard = DataCard(interface=data_interface, info=info)
data_registry.register_card(card=datacard)
```

::: opsml.PandasData
    options:
        show_root_heading: true
        show_source: true
        heading_level: 3