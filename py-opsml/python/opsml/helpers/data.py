# mypy: ignore-errors

from typing import Tuple, Union

import numpy as np
import pandas as pd
import polars as pl


def create_fake_data(
    n_samples: int = 100,
    n_features: int = 10,
    n_classes: int = 2,
    n_categorical_features: int = 0,
    task_type: str = "classification",
    random_state: int = 42,
    to_polars: bool = False,
) -> Tuple[Union[pd.DataFrame, pl.DataFrame], Union[pd.DataFrame, pl.DataFrame]]:
    """Creates fake data for testing

    Args:
        n_samples:
            Number of samples
        n_features:
            Number of features
        n_classes:
            Number of classes
        task_type:
            Task type
        random_state:
            Random state
        n_categorical_features:
            Number of categorical features
        to_polars:
            Whether to convert to polars

    Returns:
        Tuple of pd.DataFrame
    """
    num_features = n_features - n_categorical_features

    np.random.seed(random_state)
    x_data = np.random.randn(n_samples, num_features)  # pylint: disable=invalid-name

    if n_categorical_features > 0:
        cat_cols = np.random.randint(0, n_classes, size=(n_samples, n_categorical_features)).astype(str)

    y_data = np.random.randint(0, n_classes, n_samples)  # pylint: disable=invalid-name
    if task_type == "regression":
        y_data = np.random.randn(n_samples)  # pylint: disable=invalid-name

    # rename columns
    x_data = pd.DataFrame(x_data, columns=[f"col_{i}" for i in range(num_features)])  # pylint: disable=invalid-name

    if n_categorical_features > 0:
        cat_df = pd.DataFrame(cat_cols, columns=[f"cat_col_{i}" for i in range(n_categorical_features)])

        # add to X
        x_data = pd.concat([x_data, cat_df], axis=1)

    y_data = pd.DataFrame(y_data, columns=["target"])  # pylint: disable=invalid-name

    if to_polars:
        x_data = pl.from_pandas(x_data)
        y_data = pl.from_pandas(y_data)

    return x_data, y_data
