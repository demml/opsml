import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from pydantic import BaseModel
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from opsml import Card, ModelCard, ServiceCard, TaskType
from opsml.experiment import Experiment, start_experiment
from opsml.helpers.data import create_fake_data
from opsml.model import ModelSaveKwargs, TorchModel


def plot_residuals_torch(
    y_test: Union[torch.Tensor, np.ndarray],
    y_pred: Union[torch.Tensor, np.ndarray],
    style: str = "seaborn-v0_8",
    plot_size: tuple = (10, 8),
) -> plt.Figure:
    """
    Plot residuals for PyTorch model predictions.

    Args:
        y_test: True values as tensor or numpy array
        y_pred: Predicted values as tensor or numpy array
        style: Matplotlib style to use
        plot_size: Figure size as (width, height)

    Returns:
        matplotlib Figure object
    """
    # Convert tensors to numpy arrays if needed
    if isinstance(y_test, torch.Tensor):
        y_test = y_test.detach().cpu().numpy()
    if isinstance(y_pred, torch.Tensor):
        y_pred = y_pred.detach().cpu().numpy()

    # Flatten arrays if needed
    y_test = y_test.flatten()
    y_pred = y_pred.flatten()

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


class ModelParameters(BaseModel):
    """Model hyperparameters for the neural network."""

    hidden_size: int = 64
    learning_rate: float = 0.001
    batch_size: int = 32
    num_epochs: int = 50
    dropout_rate: float = 0.2


class RegressionNet(nn.Module):
    """Simple neural network for regression tasks."""

    def __init__(self, input_size: int, hidden_size: int, dropout_rate: float = 0.2):
        super(RegressionNet, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def generate_plots(model: RegressionNet, test_data: torch.FloatTensor):
    model.eval()
    with torch.no_grad():
        final_predictions = model(test_data)

    residual_fig = plot_residuals_torch(test_data, final_predictions)
    exp.log_figure(name="residual_plot", figure=residual_fig)


def create_pytorch_regression_model(
    exp: Experiment,
    X: pd.DataFrame,
    y: pd.DataFrame,
) -> ModelCard:
    """Create and train a PyTorch regression model with epoch-by-epoch logging."""

    parameters = ModelParameters()

    # Prepare data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Convert to tensors
    X_train_tensor = torch.FloatTensor(X_train_scaled)
    y_train_tensor = torch.FloatTensor(y_train.values).reshape(-1, 1)
    X_test_tensor = torch.FloatTensor(X_test_scaled)
    y_test_tensor = torch.FloatTensor(y_test.values).reshape(-1, 1)

    # Create data loaders
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(
        train_dataset, batch_size=parameters.batch_size, shuffle=True
    )

    # Initialize model
    model = RegressionNet(
        input_size=X_train.shape[1],
        hidden_size=parameters.hidden_size,
        dropout_rate=parameters.dropout_rate,
    )

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=parameters.learning_rate)

    # Log parameters
    exp.log_parameters(parameters.model_dump())

    # Training loop with epoch-by-epoch logging
    for epoch in range(parameters.num_epochs):
        model.train()
        train_loss = 0.0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)

        # Evaluate on test set
        model.eval()
        with torch.no_grad():
            test_outputs = model(X_test_tensor)
            test_loss = criterion(test_outputs, y_test_tensor).item()

            # Calculate additional metrics
            y_pred = test_outputs.numpy()
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

        # Log metrics for this epoch
        exp.log_metric(name="train_loss", value=avg_train_loss)
        exp.log_metric(name="test_loss", value=test_loss)
        exp.log_metric(name="test_mse", value=mse)
        exp.log_metric(name="test_r2", value=r2)
        exp.log_metric(name="epoch", value=float(epoch + 1))

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{parameters.num_epochs}")
            print(f"  Train Loss: {avg_train_loss:.4f}")
            print(f"  Test Loss: {test_loss:.4f}")
            print(f"  Test R²: {r2:.4f}")

    # Create model interface
    sample_data = torch.FloatTensor(X_train_scaled[:10])

    model_interface = TorchModel(
        model=model,
        sample_data=sample_data,
        task_type=TaskType.Regression,
        preprocessor=scaler,
    )

    modelcard = ModelCard(
        interface=model_interface,
        space="opsml",
        name="pytorch_regression_model",
        tags=["pytorch", "regression", "neural_network"],
    )

    # Register model
    exp.register_card(card=modelcard, save_kwargs=ModelSaveKwargs(save_onnx=True))

    return modelcard


if __name__ == "__main__":
    with start_experiment(space="opsml", name="pytorch_regression_experiment") as exp:
        # Create regression data
        X, y = create_fake_data(n_samples=1000, task_type="regression")

        # Train model
        pytorch_model = create_pytorch_regression_model(exp, X, y)

        # Create service card
        service_card = ServiceCard(
            space="opsml",
            name="pytorch_regression_service",
            cards=[Card(alias="pytorch_regression", card=pytorch_model)],
        )
        exp.register_card(service_card)
