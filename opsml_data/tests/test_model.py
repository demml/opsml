from opsml_data.connector.data_model import DataModel
from pydantic import ValidationError


def test_model(test_data_record, test_data_record_wrong):

    model = DataModel(**test_data_record)
    isinstance(model, DataModel)

    ## the following should fail
    try:
        new_model = DataModel(**test_data_record_wrong)
    except ValidationError as e:
        pass
