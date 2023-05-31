import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8889/"


from sklearn.datasets import load_linnerud
import numpy as np

# Opsml
from opsml.registry import CardInfo, DataCard
from opsml.profile import DataProfiler

data, target = load_linnerud(return_X_y=True, as_frame=True)
data["Pulse"] = target.Pulse

# Simulate creating 1st DataCard
card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
data_card = DataCard(info=card_info, data=data)
data_card.create_data_profile()

# Simulate creating 2nd DataCard
data2 = data * np.random.rand(data.shape[1])
card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
data_card2 = DataCard(info=card_info, data=data2)
data_card2.create_data_profile()

comparison = DataProfiler.compare_reports(reports=[data_card.data_profile, data_card2.data_profile])
comparison.to_file("comparison_report.html")
