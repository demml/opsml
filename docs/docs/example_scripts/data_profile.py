import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8889/"


# Data
from sklearn.datasets import load_linnerud

# Opsml
from opsml.registry import CardInfo, DataCard, CardRegistry

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse


card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
data_card = DataCard(info=card_info, data=data)

data_card.create_data_profile(sample_perc=0.5)  # you can specify a sampling percentage between 0 and 1

# if youd like to view you're report, you can export it to html or json
# Jupyter notebooks will render the html without needing to save (just call data_card.data_profile)
# data_card.data_profile.to_file("my_report.html")

# Registering card will automatically save the report and its html
data_registry = CardRegistry(registry_name="data")
data_registry.register_card(card=data_card)
