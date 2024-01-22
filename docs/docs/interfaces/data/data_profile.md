# Data Profile

## Data Profile

Opsml DataInterfaces support [ydata-profiling](https://github.com/ydataai/ydata-profiling) with an optional extra.

```bash
poetry add opsml[profiling]
```

To add a data profile to your interface you can either supply a custom data profile created through the `ydata-profiling` library or you can call the `create_data_profile` method after `DataInterface` instantiation. **Note** - you can also call `create_data_profile` from a `DataCard` after instantiation (example below). The `create_data_profile` is optimized for performance, and thus, will omit certain analyses by defualt (interactions, character/word analysis, etc.). If you'd like more control over what analyses are conducted, it is recommended that you create a custom report via `ydata-profiling` and provide it to the DataCard using the `data_profile` arg.


**Example of `create_data_profile`**

```py hl_lines="5 13 19"
# Data
from sklearn.datasets import load_linnerud

# Opsml
from opsml import CardInfo, DataCard, CardRegistry, PandasData

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

interface = PandasData(data=data)

# create data profile from interface
interface.create_data_profile(sample_perc=0.5) # you can specify a sampling percentage between 0 and 1

card_info = CardInfo(name="linnerrud", repository="opsml", contact="user@email.com")
data_card = DataCard(info=card_info, data=data)

# this also works
data_card.create_data_profile(sample_perc=0.5) 

# if youd like to view you're report, you can export it to html or json
# Jupyter notebooks will render the html without needing to save (just call data_card.data_profile)
# data_card.data_profile.to_file("my_report.html")

# Registering card will automatically save the report and its html
data_registry = CardRegistry(registry_name="data")
data_registry.register_card(card=data_card)
```

**Example of providing your own custom data profile**

```python hl_lines="1 8"
from ydata_profiling import ProfileReport
from opsml import PandasData 

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

data_profile = ProfileReport(data, title="Profiling Report")
interface = PandasData(data=data, data_profile=data_profile)
```

### Comparing data profiles

You can also leverage `Opsmls` thin profiling wrapper for comparing different data profiles


```py hl_lines="6 13 19 21"
from sklearn.datasets import load_linnerud
import numpy as np

# Opsml
from opsml import PandasData
from opsml.profile import DataProfiler

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

# Simulate creating 1st DataCard
interface = PandasData(data=data)
interface.create_data_profile()

# Simulate creating 2nd DataCard
data2 = data * np.random.rand(data.shape[1])
card_info = CardInfo(name="linnerrud", repository="opsml", contact="user@email.com")
interface2 = PandasData(data=data)
interface2.create_data_profile()

comparison = DataProfiler.compare_reports(reports=[data_card.data_profile, data_card2.data_profile])
comparison.to_file("comparison_report.html")
```

### Docs

::: opsml.profile.DataProfiler
    options:
        members:
            - create_profile_report
            - compare_reports
        show_root_heading: true
        show_source: true
        heading_level: 3