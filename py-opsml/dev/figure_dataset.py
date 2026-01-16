# type: ignore
from datetime import datetime, timedelta

import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats


def generate_sales_data_with_promo_adjustment(
    base_demand: int = 1000,
    n_rows: int = 5000,
    competitor_price_effect: float = -50.0,
):
    """
    Generates a synthetic dataset for predicting apple sales demand with multiple
    influencing factors.

    This function creates a pandas DataFrame with features relevant to apple sales.
    The features include date, average_temperature, rainfall, weekend flag, holiday flag,
    promotional flag, price_per_kg, competitor's price, marketing intensity, stock availability,
    and the previous day's demand. The target variable, 'demand', is generated based on a
    combination of these features with some added noise.

    Args:
        base_demand (int, optional): Base demand for apples. Defaults to 1000.
        n_rows (int, optional): Number of rows (days) of data to generate. Defaults to 5000.
        competitor_price_effect (float, optional): Effect of competitor's price being lower
                                                   on our sales. Defaults to -50.

    Returns:
        pd.DataFrame: DataFrame with features and target variable for apple sales prediction.

    Example:
        >>> df = generate_apple_sales_data_with_promo_adjustment(base_demand=1200, n_rows=6000)
        >>> df.head()
    """

    # Set seed for reproducibility
    np.random.seed(9999)

    # Create date range
    dates = [datetime.now() - timedelta(days=i) for i in range(n_rows)]
    dates.reverse()

    # Generate features
    df = pd.DataFrame(
        {
            "date": dates,
            "average_temperature": np.random.uniform(10, 35, n_rows),
            "rainfall": np.random.exponential(5, n_rows),
            "weekend": [(date.weekday() >= 5) * 1 for date in dates],
            "holiday": np.random.choice([0, 1], n_rows, p=[0.97, 0.03]),
            "price_per_kg": np.random.uniform(0.5, 3, n_rows),
            "month": [date.month for date in dates],
        }
    )

    # Introduce inflation over time (years)
    df["inflation_multiplier"] = (
        1 + (df["date"].dt.year - df["date"].dt.year.min()) * 0.03
    )

    # Incorporate seasonality due to apple harvests
    df["harvest_effect"] = np.sin(2 * np.pi * (df["month"] - 3) / 12) + np.sin(
        2 * np.pi * (df["month"] - 9) / 12
    )

    # Modify the price_per_kg based on harvest effect
    df["price_per_kg"] = df["price_per_kg"] - df["harvest_effect"] * 0.5

    # Adjust promo periods to coincide with periods lagging peak harvest by 1 month
    peak_months = [4, 10]  # months following the peak availability
    df["promo"] = np.where(
        df["month"].isin(peak_months),
        1,
        np.random.choice([0, 1], n_rows, p=[0.85, 0.15]),
    )

    # Generate target variable based on features
    base_price_effect = -df["price_per_kg"] * 50
    seasonality_effect = df["harvest_effect"] * 50
    promo_effect = df["promo"] * 200

    df["demand"] = (
        base_demand
        + base_price_effect
        + seasonality_effect
        + promo_effect
        + df["weekend"] * 300
        + np.random.normal(0, 50, n_rows)
    ) * df["inflation_multiplier"]  # adding random noise

    # Add previous day's demand
    df["previous_days_demand"] = df["demand"].shift(1)
    df["previous_days_demand"].fillna(
        method="bfill", inplace=True
    )  # fill the first row

    # Introduce competitor pricing
    df["competitor_price_per_kg"] = np.random.uniform(0.5, 3, n_rows)
    df["competitor_price_effect"] = (
        df["competitor_price_per_kg"] < df["price_per_kg"]
    ) * competitor_price_effect

    # Stock availability based on past sales price (3 days lag with logarithmic decay)
    log_decay = -np.log(df["price_per_kg"].shift(3) + 1) + 2
    df["stock_available"] = np.clip(log_decay, 0.7, 1)

    # Marketing intensity based on stock availability
    # Identify where stock is above threshold
    high_stock_indices = df[df["stock_available"] > 0.95].index

    # For each high stock day, increase marketing intensity for the next week
    for idx in high_stock_indices:
        df.loc[idx : min(idx + 7, n_rows - 1), "marketing_intensity"] = (
            np.random.uniform(0.7, 1)
        )

    # If the marketing_intensity column already has values, this will preserve them;
    #  if not, it sets default values
    fill_values = pd.Series(np.random.uniform(0, 0.5, n_rows), index=df.index)
    df["marketing_intensity"].fillna(fill_values, inplace=True)

    # Adjust demand with new factors
    df["demand"] = (
        df["demand"] + df["competitor_price_effect"] + df["marketing_intensity"]
    )

    # Drop temporary columns
    df.drop(
        columns=[
            "inflation_multiplier",
            "harvest_effect",
            "month",
            "competitor_price_effect",
            "stock_available",
        ],
        inplace=True,
    )

    return df


def plot_time_series_demand(
    data, window_size=7, style="seaborn-v0_8", plot_size=(16, 12)
):
    if not isinstance(data, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    df = data.copy()

    df["date"] = pd.to_datetime(df["date"])

    # Calculate the rolling average
    df["rolling_avg"] = df["demand"].rolling(window=window_size).mean()

    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)
        # Plot the original time series data with low alpha (transparency)
        ax.plot(df["date"], df["demand"], "b-o", label="Original Demand", alpha=0.15)
        # Plot the rolling average
        ax.plot(
            df["date"],
            df["rolling_avg"],
            "r",
            label=f"{window_size}-Day Rolling Average",
        )

        # Set labels and title
        ax.set_title(
            f"Time Series Plot of Demand with {window_size} day Rolling Average",
            fontsize=14,
        )
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Demand", fontsize=12)

        # Add legend to explain the lines
        ax.legend()
        plt.tight_layout()

    plt.close(fig)
    return fig


def plot_box_weekend(df, style="seaborn-v0_8", plot_size=(10, 8)):
    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)
        sns.boxplot(data=df, x="weekend", y="demand", ax=ax, color="lightgray")
        sns.stripplot(
            data=df,
            x="weekend",
            y="demand",
            ax=ax,
            hue="weekend",
            palette={0: "blue", 1: "green"},
            alpha=0.15,
            jitter=0.3,
            size=5,
        )

        ax.set_title("Box Plot of Demand on Weekends vs. Weekdays", fontsize=14)
        ax.set_xlabel("Weekend (0: No, 1: Yes)", fontsize=12)
        ax.set_ylabel("Demand", fontsize=12)
        for i in ax.get_xticklabels() + ax.get_yticklabels():
            i.set_fontsize(10)
        ax.legend_.remove()
        plt.tight_layout()
    plt.close(fig)
    return fig


def plot_scatter_demand_price(df, style="seaborn-v0_8", plot_size=(10, 8)):
    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)
        # Scatter plot with jitter, transparency, and color-coded based on weekend
        sns.scatterplot(
            data=df,
            x="price_per_kg",
            y="demand",
            hue="weekend",
            palette={0: "blue", 1: "green"},
            alpha=0.15,
            ax=ax,
        )
        # Fit a simple regression line for each subgroup
        sns.regplot(
            data=df[df["weekend"] == 0],
            x="price_per_kg",
            y="demand",
            scatter=False,
            color="blue",
            ax=ax,
        )
        sns.regplot(
            data=df[df["weekend"] == 1],
            x="price_per_kg",
            y="demand",
            scatter=False,
            color="green",
            ax=ax,
        )

        ax.set_title(
            "Scatter Plot of Demand vs Price per kg with Regression Line", fontsize=14
        )
        ax.set_xlabel("Price per kg", fontsize=12)
        ax.set_ylabel("Demand", fontsize=12)
        for i in ax.get_xticklabels() + ax.get_yticklabels():
            i.set_fontsize(10)
        plt.tight_layout()
    plt.close(fig)
    return fig


def plot_density_weekday_weekend(df, style="seaborn-v0_8", plot_size=(10, 8)):
    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)

        # Plot density for weekdays
        sns.kdeplot(
            df[df["weekend"] == 0]["demand"],
            color="blue",
            label="Weekday",
            ax=ax,
            fill=True,
            alpha=0.15,
        )

        # Plot density for weekends
        sns.kdeplot(
            df[df["weekend"] == 1]["demand"],
            color="green",
            label="Weekend",
            ax=ax,
            fill=True,
            alpha=0.15,
        )

        ax.set_title("Density Plot of Demand by Weekday/Weekend", fontsize=14)
        ax.set_xlabel("Demand", fontsize=12)
        ax.legend(fontsize=12)
        for i in ax.get_xticklabels() + ax.get_yticklabels():
            i.set_fontsize(10)

        plt.tight_layout()
    plt.close(fig)
    return fig


def plot_coefficients(model, feature_names, style="seaborn-v0_8", plot_size=(10, 8)):
    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)
        ax.barh(feature_names, model.coef_)
        ax.set_title("Coefficient Plot", fontsize=14)
        ax.set_xlabel("Coefficient Value", fontsize=12)
        ax.set_ylabel("Features", fontsize=12)
        plt.tight_layout()
    plt.close(fig)
    return fig


def plot_residuals(y_test, y_pred, style="seaborn-v0_8", plot_size=(10, 8)):
    residuals = y_test - y_pred

    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)
        sns.residplot(
            x=y_pred,
            y=residuals,
            lowess=True,
            ax=ax,
            line_kws={"color": "red", "lw": 1},
        )

        ax.axhline(y=0, color="black", linestyle="--")
        ax.set_title("Residual Plot", fontsize=14)
        ax.set_xlabel("Predicted values", fontsize=12)
        ax.set_ylabel("Residuals", fontsize=12)

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(10)

        plt.tight_layout()

    plt.close(fig)
    return fig


def plot_prediction_error(y_test, y_pred, style="seaborn-v0_8", plot_size=(10, 8)):
    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)
        ax.scatter(y_pred, y_test - y_pred)
        ax.axhline(y=0, color="red", linestyle="--")
        ax.set_title("Prediction Error Plot", fontsize=14)
        ax.set_xlabel("Predicted Values", fontsize=12)
        ax.set_ylabel("Errors", fontsize=12)
        plt.tight_layout()
    plt.close(fig)
    return fig


def plot_qq(y_test, y_pred, style="seaborn-v0_8", plot_size=(10, 8)):
    residuals = y_test - y_pred
    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)
        stats.probplot(residuals, dist="norm", plot=ax)
        ax.set_title("QQ Plot", fontsize=14)
        plt.tight_layout()
    plt.close(fig)
    return fig


def plot_correlation_matrix(df, style="seaborn-v0_8", plot_size=(10, 8)):
    with plt.style.context(style=style):
        fig, ax = plt.subplots(figsize=plot_size)

        # Calculate the correlation matrix
        corr = df.corr()

        # Generate a mask for the upper triangle
        mask = np.triu(np.ones_like(corr, dtype=bool))

        # Draw the heatmap with the mask and correct aspect ratio
        sns.heatmap(
            corr,
            mask=mask,
            cmap="coolwarm",
            vmax=0.3,
            center=0,
            square=True,
            linewidths=0.5,
            annot=True,
            fmt=".2f",
        )

        ax.set_title("Feature Correlation Matrix", fontsize=14)
        plt.tight_layout()

    plt.close(fig)
    # convert to filesystem path spec for os compatibility
    return fig
