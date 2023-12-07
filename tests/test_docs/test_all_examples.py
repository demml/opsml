from opsml.projects import ProjectInfo, OpsmlProject
from opsml.registry import ModelCard, DataCard
from sklearn import linear_model


def test_challenger_example(opsml_project: OpsmlProject):
    ########### Challenger example

    from sklearn.datasets import load_linnerud
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression, Lasso, PoissonRegressor
    from sklearn.metrics import mean_absolute_error
    import numpy as np

    # Opsml
    from opsml.registry import CardInfo, DataCard, CardRegistry, DataSplit, ModelCard
    from opsml.projects import ProjectInfo
    from opsml.model.challenger import ModelChallenger

    ### **Create Example Data**

    data, target = load_linnerud(return_X_y=True, as_frame=True)
    data["Pulse"] = target.Pulse

    # Split indices
    indices = np.arange(data.shape[0])

    # usual train-val split
    train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)
    card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")

    # Create card
    datacard = DataCard(
        info=card_info,
        data=data,
        dependent_vars=["Pulse"],
        data_splits=[
            DataSplit(label="train", indices=train_idx),
            DataSplit(label="test", indices=test_idx),
        ],
    )
    data_reg = CardRegistry(registry_name="data")
    data_reg.register_card(card=datacard)

    ProjectInfo(name="opsml", team="devops", user_email="test_email")
    with opsml_project.run(run_name="challenger-lin-reg") as run:
        datacard = data_reg.load_card(uid=datacard.uid)
        splits = datacard.split_data()

        reg = LinearRegression()
        reg.fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        run.log_metric("mae", value=mae)

        model_card = ModelCard(
            trained_model=reg,
            sample_input_data=splits.train.X[0:1],
            name="linear_reg",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
            to_onnx=True,
        )
        run.register_card(card=model_card)

    ProjectInfo(name="opsml", team="devops", user_email="test_email")
    with opsml_project.run(run_name="challenger-lasso") as run:
        datacard = data_reg.load_card(uid=datacard.uid)
        splits = datacard.split_data()

        reg = Lasso()
        reg.fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        run.log_metric("mae", value=mae)

        model_card = ModelCard(
            trained_model=reg,
            sample_input_data=splits.train.X[0:1],
            name="lasso_reg",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
            to_onnx=True,
        )
        run.register_card(card=model_card)

    ProjectInfo(name="opsml", team="devops", user_email="test_email")
    with opsml_project.run(run_name="challenger-poisson") as run:
        datacard = data_reg.load_card(uid=datacard.uid)
        splits = datacard.split_data()

        reg = PoissonRegressor()
        reg.fit(splits.train.X.to_numpy(), splits.train.y)

        reg_preds = reg.predict(splits.test.X.to_numpy())
        mae = mean_absolute_error(splits.test.y.to_numpy(), reg_preds)
        run.log_metric("mae", value=mae)

        model_card = ModelCard(
            trained_model=reg,
            sample_input_data=splits.train.X[0:1],
            name="poisson_reg",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=datacard.uid,
            tags={"example": "challenger"},
            to_onnx=True,
        )
        run.register_card(card=model_card)

    model_registry = CardRegistry(registry_name="model")
    linreg_card = model_registry.load_card(
        name="linear_reg",
        tags={"example": "challenger"},
    )

    challenger = ModelChallenger(challenger=linreg_card)

    reports = challenger.challenge_champion(
        metric_name="mae",
        lower_is_better=True,
        champions=[
            CardInfo(name="lasso_reg", team="mlops", version="1.0.0"),
            CardInfo(name="poisson_reg", team="mlops", version="1.0.0"),
        ],
    )

    print([report.model_dump() for report in reports["mae"]])


def test_datacard(db_registries):
    from sklearn.datasets import load_linnerud
    from sklearn.model_selection import train_test_split
    import numpy as np

    # Opsml
    from opsml.registry import CardInfo, DataCard, DataSplit

    data, target = load_linnerud(return_X_y=True, as_frame=True)
    data["Pulse"] = target.Pulse

    # Split indices
    indices = np.arange(data.shape[0])

    # usual train-val split
    train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

    card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
    data_card = DataCard(
        info=card_info,
        data=data,
        dependent_vars=["Pulse"],
        # define splits
        data_splits=[
            DataSplit(label="train", indices=train_idx),
            DataSplit(label="test", indices=test_idx),
        ],
    )

    # splits look good
    splits = data_card.split_data()
    print(splits.train.X.head())

    data_registry = db_registries["data"]
    data_registry.register_card(card=data_card)
    print(data_card.version)
    # > 1.0.0

    # list cards
    cards = data_registry.list_cards(
        uid=data_card.uid,
        as_dataframe=False,
    )  # can also supply, name, team, version
    print(cards[0])


def test_data_splits():
    import polars as pl
    from opsml.registry import DataCard, DataSplit, CardInfo

    info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

    df = pl.DataFrame(
        {
            "foo": [1, 2, 3, 4, 5, 6],
            "bar": ["a", "b", "c", "d", "e", "f"],
            "y": [1, 2, 3, 4, 5, 6],
        }
    )

    datacard = DataCard(
        info=info,
        data=df,
        data_splits=[
            DataSplit(label="train", column_name="foo", column_value=6, inequality="<"),
            DataSplit(label="test", column_name="foo", column_value=6),
        ],
    )

    splits = datacard.split_data()
    assert splits.train.X.shape[0] == 5
    assert splits.test.X.shape[0] == 1

    import numpy as np
    from opsml.registry import DataCard, DataSplit, CardInfo

    info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

    data = np.random.rand(10, 10)

    datacard = DataCard(info=info, data=data, data_splits=[DataSplit(label="train", indices=[0, 1, 5])])

    splits = datacard.split_data()
    assert splits.train.X.shape[0] == 3

    #### **Start and Stop Slicing**

    import numpy as np
    from opsml.registry import DataCard, DataSplit, CardInfo

    info = CardInfo(name="data", team="mlops", user_email="user@mlops.com")

    data = np.random.rand(10, 10)

    datacard = DataCard(info=info, data=data, data_splits=[DataSplit(label="train", start=0, stop=3)])

    splits = datacard.split_data()
    assert splits.train.X.shape[0] == 3


def test_data_profile(db_registries):
    # Data
    from sklearn.datasets import load_linnerud

    # Opsml
    from opsml.registry import CardInfo, DataCard

    data, target = load_linnerud(return_X_y=True, as_frame=True)
    data["Pulse"] = target.Pulse

    card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
    data_card = DataCard(info=card_info, data=data)

    data_card.create_data_profile(sample_perc=0.5)  # you can specify a sampling percentage between 0 and 1

    # if youd like to view you're report, you can export it to html or json
    # Jupyter notebooks will render the html without needing to save (just call data_card.data_profile)
    # data_card.data_profile.to_file("my_report.html")

    # Registering card will automatically save the report and its html
    data_registry = db_registries["data"]
    data_registry.register_card(card=data_card)

    from ydata_profiling import ProfileReport
    from opsml.registry import DataCard

    data, target = load_linnerud(return_X_y=True, as_frame=True)
    data["Pulse"] = target.Pulse

    data_profile = ProfileReport(data, title="Profiling Report")

    card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")
    data_card = DataCard(info=card_info, data=data, data_profile=data_profile)

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

    DataProfiler.compare_reports(reports=[data_card.data_profile, data_card2.data_profile])
    # comparison.to_file("comparison_report.html")


def test_modelcard(db_registries):
    # load data card from earlier
    from sklearn.linear_model import LinearRegression

    # Opsml
    from opsml.registry import ModelCard, CardInfo

    # set up registries
    data_registry = db_registries["data"]
    model_registry = db_registries["model"]

    card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")

    # load datacard
    datacard = data_registry.load_card(name=card_info.name, version="1.0.0")

    # data is not loaded by default (helps when sharing cards with large data)
    datacard.load_data()
    data_splits = datacard.split_data()

    X_train = data_splits.train.X
    y_train = data_splits.train.y

    # fit model
    linreg = LinearRegression()
    linreg = linreg.fit(X=X_train, y=y_train)

    # lets test the onnx model before registering
    modelcard = ModelCard(
        info=card_info,
        trained_model=linreg,
        sample_input_data=X_train,
        datacard_uid=datacard.uid,
        to_onnx=True,
    )

    onnx_predictor = modelcard.onnx_model()
    record = list(modelcard.sample_input_data[0:1].T.to_dict().values())[0]

    pred_onnx = onnx_predictor.predict(record)["value"]
    pred_orig = onnx_predictor.predict_with_model(linreg, record)[0][0]

    print(f"Original: {pred_orig}, Onnx: {pred_onnx}")
    # > Original: 54.4616866, Onnx: 54.4616866

    print(onnx_predictor.input_sig.model_json_schema())
    print(onnx_predictor.output_sig.model_json_schema())

    # everything looks good
    model_registry.register_card(modelcard)


def test_custom_onnx(db_registries):
    import tempfile

    from torch import nn
    import torch.utils.model_zoo as model_zoo
    import torch.onnx
    import onnx

    # Super Resolution model definition in PyTorch
    import torch.nn as nn
    import torch.nn.init as init

    ## opsml
    from opsml.model.types import OnnxModelDefinition
    from opsml.registry import CardRegistries, ModelCard, DataCard

    registries = CardRegistries()
    registries.data = db_registries["data"]
    registries.model = db_registries["model"]

    class SuperResolutionNet(nn.Module):
        def __init__(self, upscale_factor, inplace=False):
            super(SuperResolutionNet, self).__init__()

            self.relu = nn.ReLU(inplace=inplace)
            self.conv1 = nn.Conv2d(1, 64, (5, 5), (1, 1), (2, 2))
            self.conv2 = nn.Conv2d(64, 64, (3, 3), (1, 1), (1, 1))
            self.conv3 = nn.Conv2d(64, 32, (3, 3), (1, 1), (1, 1))
            self.conv4 = nn.Conv2d(32, upscale_factor**2, (3, 3), (1, 1), (1, 1))
            self.pixel_shuffle = nn.PixelShuffle(upscale_factor)

            self._initialize_weights()

        def forward(self, x):
            x = self.relu(self.conv1(x))
            x = self.relu(self.conv2(x))
            x = self.relu(self.conv3(x))
            x = self.pixel_shuffle(self.conv4(x))
            return x

        def _initialize_weights(self):
            init.orthogonal_(self.conv1.weight, init.calculate_gain("relu"))
            init.orthogonal_(self.conv2.weight, init.calculate_gain("relu"))
            init.orthogonal_(self.conv3.weight, init.calculate_gain("relu"))
            init.orthogonal_(self.conv4.weight)

    # Create the super-resolution model by using the above model definition.
    torch_model = SuperResolutionNet(upscale_factor=3)

    # Load pretrained model weights
    model_url = "https://s3.amazonaws.com/pytorch/test_data/export/superres_epoch100-44c6958e.pth"
    batch_size = 1  # just a random number

    # Initialize model with the pretrained weights
    def map_location(storage, loc):
        return storage
    if torch.cuda.is_available():
        map_location = None
    torch_model.load_state_dict(model_zoo.load_url(model_url, map_location=map_location))

    # set the model to inference mode
    torch_model.eval()

    # Input to the model
    x = torch.randn(batch_size, 1, 224, 224, requires_grad=True)
    torch_model(x)

    # Export the model
    with tempfile.TemporaryDirectory() as tmpdir:
        onnx_path = f"{tmpdir}/super_resolution.onnx"
        torch.onnx.export(
            torch_model,  # model being run
            x,  # model input (or a tuple for multiple inputs)
            onnx_path,  # where to save the model (can be a file or file-like object)
            export_params=True,  # store the trained parameter weights inside the model file
            opset_version=10,  # the ONNX version to export the model to
            do_constant_folding=True,  # whether to execute constant folding for optimization
            input_names=["input"],  # the model's input names
            output_names=["output"],  # the model's output names
            dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},  # variable length axes
        )

        onnx_model = onnx.load(onnx_path)

    ######## Create DataCard
    datacard = DataCard(
        name="image-data",
        team="opsml",
        user_email="user@opsml.com",
        data=x.detach().numpy(),
    )
    registries.data.register_card(datacard)

    ####### Create ModelCard

    model_def = OnnxModelDefinition(
        onnx_version="1.14.0",
        model_bytes=onnx_model.SerializeToString(),
    )

    ModelCard(
        name="pytorch-custom-onnx",
        team="opsml",
        user_email="opsml.com",
        trained_model=torch_model,
        sample_input_data=datacard.data[0:1],
        onnx_model_def=model_def,
        datacard_uid=datacard.uid,
        to_onnx=True,
    )

    # remove final registration line due to pytest module-level save issues


def test_overview_list(
    linear_regression: linear_model.LinearRegression,
    db_registries,
):
    data_registry = db_registries["data"]
    model, data = linear_regression
    data_card = DataCard(
        data=data,
        name="reg_data",
        team="mlops",
        user_email="mlops.com",
    )
    data_registry.register_card(card=data_card)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="linear-reg",
        team="opsml",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        version="1.0.0",
        to_onnx=True,
    )
    model_registry = db_registries["model"]
    model_registry.register_card(card=model_card)
    uid = model_card.uid

    ######## Doc example
    registry = db_registries["model"]

    registry.list_cards()
    # will list all cards in registry

    registry.list_cards(limit=10)
    # will list cards and limit the result to 10

    registry.list_cards(name="linear-reg")
    # list all cards with name "linear-reg"

    registry.list_cards(name="linear-reg", team="opsml")
    # list all cards with name "linear-reg" with team "opsml"

    registry.list_cards(name="linear-reg", team="opsml", version="1.0.0")
    # list card with name "linear-reg" with team "opsml" and version 1.0.0

    registry.list_cards(name="linear-reg", team="opsml", version="1.*.*")
    # list cards with name "linear-reg" with team "opsml" and major version of "1"

    registry.list_cards(name="linear-reg", team="opsml", version="^2.3.4")
    # list card with name "linear-reg" with team "opsml" and latest version < 3.0.0

    registry.list_cards(name="linear-reg", team="opsml", version="~2.3.4")
    # list card with name "linear-reg" with team "opsml" and latest version < 2.4.0

    registry.list_cards(uid=uid, as_dataframe=True)


def test_runcard_opsml_example(opsml_project: OpsmlProject):
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import Lasso
    from sklearn.metrics import mean_absolute_percentage_error

    # from opsml.projects import OpsmlProject, ProjectInfo
    from opsml.registry import CardInfo, DataCard, ModelCard

    card_info = CardInfo(name="linear-reg", team="opsml", user_email="user@email.com")

    # to use runs, you must create and use a project
    ProjectInfo(name="opsml-dev", team="opsml", user_email="user@email.com")
    # project = OpsmlProject(info=project_info)
    project = opsml_project

    def create_fake_data():
        X_train = np.random.normal(-4, 2.0, size=(1000, 10))

        col_names = []
        for i in range(0, X_train.shape[1]):
            col_names.append(f"col_{i}")

        X = pd.DataFrame(X_train, columns=col_names)
        y = np.random.randint(1, 10, size=(1000, 1))

        return X, y

    # start the run
    with project.run(run_name="optional_run_name") as run:
        X, y = create_fake_data()

        # train model
        lasso = Lasso(alpha=0.5)
        lasso = lasso.fit(X.to_numpy(), y)

        preds = lasso.predict(X.to_numpy())

        mape = mean_absolute_percentage_error(y, preds)

        # Create metrics / params
        run.log_metric(key="mape", value=mape)
        run.log_parameter(key="alpha", value=0.5)

        data_card = DataCard(data=X, info=card_info)
        run.register_card(card=data_card, version_type="major")  # you can specify "major", "minor", "patch"

        model_card = ModelCard(
            trained_model=lasso,
            sample_input_data=X,
            datacard_uid=data_card.uid,
            info=card_info,
            to_onnx=True,
        )
        run.register_card(card=model_card)

    print(run.runcard.get_metric("mape"))
    # > Metric(name='mape', value=0.8489706297619047, step=None, timestamp=None)

    print(run.runcard.get_parameter("alpha"))
    # > Param(name='alpha', value=0.5)


def test_index_example(db_registries):
    from sklearn.datasets import load_linnerud
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    import numpy as np

    # Opsml
    from opsml.registry import CardInfo, DataCard, ModelCard, DataSplit

    # set up registries
    data_registry = db_registries["data"]
    model_registry = db_registries["model"]

    # card info (optional, but is used to simplify required args a bit)
    card_info = CardInfo(name="linnerrud", team="opsml", user_email="user@email.com")

    # get X, y
    data, target = load_linnerud(return_X_y=True, as_frame=True)
    data["Pulse"] = target.Pulse

    # Split indices
    indices = np.arange(data.shape[0])

    # usual train-test split
    train_idx, test_idx = train_test_split(indices, test_size=0.2, train_size=None)

    datacard = DataCard(
        info=card_info,
        data=data,
        dependent_vars=["Pulse"],
        # define splits
        data_splits=[
            DataSplit(label="train", indices=train_idx),
            DataSplit(label="test", indices=test_idx),
        ],
    )

    # register card
    data_registry.register_card(datacard)

    # split data
    data_splits = datacard.split_data()
    X_train = data_splits.train.X
    y_train = data_splits.train.y

    # fit model
    linreg = LinearRegression()
    linreg = linreg.fit(X=X_train, y=y_train)

    # Create ModelCard
    modelcard = ModelCard(
        info=card_info,
        trained_model=linreg,
        sample_input_data=X_train,
        datacard_uid=datacard.uid,
        to_onnx=True,
    )

    model_registry.register_card(card=modelcard)
    print(data_registry.list_cards(info=card_info))
    print(model_registry.list_cards(info=card_info))


def test_quickstart(opsml_project: OpsmlProject):
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    import numpy as np

    from opsml.projects import ProjectInfo
    from opsml.registry import DataCard, ModelCard

    def fake_data():
        X_train = np.random.normal(-4, 2.0, size=(1000, 10))

        col_names = []
        for i in range(0, X_train.shape[1]):
            col_names.append(f"col_{i}")

        X = pd.DataFrame(X_train, columns=col_names)
        y = np.random.randint(1, 10, size=(1000, 1))
        return X, y

    ProjectInfo(
        name="opsml",
        team="devops",
        user_email="test_email",
    )

    # start opsmlrun
    project = opsml_project
    with project.run(run_name="test-run") as run:
        # create data and train model
        X, y = fake_data()
        reg = LinearRegression().fit(X.to_numpy(), y)

        # Create and registry DataCard with data profile
        data_card = DataCard(
            data=X,
            name="pipeline-data",
            team="mlops",
            user_email="mlops.com",
        )
        data_card.create_data_profile()
        run.register_card(card=data_card)

        # Create and register ModelCard with auto-converted onnx model
        model_card = ModelCard(
            trained_model=reg,
            sample_input_data=X[0:1],
            name="linear_reg",
            team="mlops",
            user_email="mlops.com",
            datacard_uid=data_card.uid,
            tags={"name": "model_tag"},
            to_onnx=True,
        )
        run.register_card(card=model_card)

        # log some metrics
        for i in range(0, 10):
            run.log_metric("mape", i, step=i)
