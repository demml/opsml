from opsml.scouter.evaluate import AssertionTask, ComparisonOperator
from opsml.helpers.data import create_fake_data
from sklearn.preprocessing import StandardScaler  # type: ignore
from sklearn import ensemble  # type: ignore
from opsml.scouter.drift import (
    PsiDriftConfig,
    GenAIEvalRecord,
)
import random
import string
from figure_dataset import (  # type: ignore
    generate_sales_data_with_promo_adjustment,
    plot_box_weekend,
    plot_correlation_matrix,
    plot_density_weekday_weekend,
    plot_scatter_demand_price,
    plot_time_series_demand,
)
from opsml.experiment import Experiment
import numpy as np
from opsml.data import ColType, ColumnSplit, DataSplit
from opsml.types import DataType
from opsml.model import TaskType
from opsml import (
    PandasData,
    SklearnModel,
    Prompt,
)
import pathlib

CWD = pathlib.Path(__file__).parent
fig_path = CWD / "assets"

fig1_path = fig_path / "time_series_demand.png"
fig2_path = fig_path / "box_weekend.png"
fig3_path = fig_path / "scatter_demand.png"
fig4_path = fig_path / "weekday_weekend.png"
fig5_path = fig_path / "correlation.png"


X, y = create_fake_data(n_samples=2000)

X2, y2 = create_fake_data(
    n_samples=10_000,
    n_features=20,
    n_categorical_features=5,
    n_classes=50,
)

SAVE_PATH = CWD / "assets" / "temp_save"


def create_genai_tasks() -> list[AssertionTask]:
    """Helper function for creating genai evaluation tasks."""

    check_foo = AssertionTask(
        id="check_foo",
        field_path="response",
        operator=ComparisonOperator.Equals,
        expected_value="foo",
        description="Check that the response is 'foo'",
        condition=True,
    )

    check_bar = AssertionTask(
        id="check_bar",
        field_path="response",
        operator=ComparisonOperator.Equals,
        expected_value="bar",
        description="Check that the response is 'bar'",
        condition=True,
    )

    check_foo_1 = AssertionTask(
        id="check_foo_1",
        field_path="value",
        operator=ComparisonOperator.GreaterThan,
        expected_value=5,
        description="Check that the value is 'foo'",
        depends_on=["check_foo"],
    )

    check_foo_2 = AssertionTask(
        id="check_foo_2",
        field_path="value",
        operator=ComparisonOperator.GreaterThan,
        expected_value=10,
        description="Check that the value is 'foo'",
        depends_on=["check_foo", "check_foo_1"],
    )

    check_bar_1 = AssertionTask(
        id="check_bar_1",
        field_path="value",
        operator=ComparisonOperator.GreaterThan,
        expected_value=5,
        description="Check that the value is 'bar'",
        depends_on=["check_bar"],
    )

    return [check_foo, check_bar, check_foo_1, check_foo_2, check_bar_1]


def create_random_genaieval_record() -> GenAIEvalRecord:
    """Helper function to create a random GenAIEvalRecord for testing."""
    rand_num = np.random.rand()
    if rand_num < 0.5:
        context = {"response": "foo", "value": 15}
    else:
        context = {"response": "bar", "value": 8}

    record = GenAIEvalRecord(
        id=random_name(),  # this is optional
        context=context,
    )

    return record


def create_sklearn_interface() -> SklearnModel:
    """ "Helper function to create a random forest classifier with drift profiles.
    This function creates a random forest classifier and adds a PSI drift profile to it.
    """
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X.to_numpy(), y.to_numpy().ravel())

    model = SklearnModel(
        model=reg,
        sample_data=X,
        task_type=TaskType.Classification,
        preprocessor=StandardScaler(),
    )

    # create psi
    model.create_drift_profile(
        alias="psi",
        data=X,
        config=PsiDriftConfig(),
        data_type=DataType.Pandas,
    )

    return model


def create_pandas_data() -> PandasData:
    split = DataSplit(
        label="train",
        column_split=ColumnSplit(
            column_name="col_1",
            column_value=0.4,
            column_type=ColType.Builtin,
            inequality="<=",
        ),
    )

    modified_data = X2.copy()  # type: ignore
    # add a new column that is assigned a letter of the alphabet
    modified_data["col_2"] = np.random.choice(
        ["word1", "word2", "word3", "word4", "word5", "a", "b", "c"],
        size=len(modified_data),
    )

    interface = PandasData(
        data=modified_data,
        data_splits=[split],
        dependent_vars=["col_2"],
    )

    interface.create_data_profile(compute_correlations=False)

    return interface


def create_chat_prompt() -> Prompt:
    prompt = Prompt(
        model="gpt-4o",
        provider="openai",
        messages="what is 2 + ${variable1} and ${variable2}?",
        system_instructions="You are a helpful assistant.",
    )

    return prompt


def generate_plots(exp: Experiment):
    """Generate and log plots to the given experiment."""
    my_data = generate_sales_data_with_promo_adjustment(
        base_demand=1000,
        n_rows=10_000,
        competitor_price_effect=-25.0,
    )

    plot_time_series_demand(my_data, window_size=28).savefig(fig1_path)
    plot_box_weekend(my_data).savefig(fig2_path)
    plot_scatter_demand_price(my_data).savefig(fig3_path)
    plot_density_weekday_weekend(my_data).savefig(fig4_path)
    plot_correlation_matrix(my_data).savefig(fig5_path)

    exp.log_figure_from_path(fig1_path)
    exp.log_figure_from_path(fig2_path)
    exp.log_figure_from_path(fig3_path)
    exp.log_figure_from_path(fig4_path)
    exp.log_figure_from_path(fig5_path)


def random_name():
    """ "Generate a random string of letters for use as a name."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(10))
