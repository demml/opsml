# Overview

The Opsml examples directory contains various examples demonstrating how to use Opsml.

## Folder Structure

### Data
- `data/`: Contains examples of how to use Opsml to create DataCards for a variety of data types.
  - `arrow_data.py`: Example of creating a DataCard for Arrow data.
  - `custom_data.py`: Example of creating a custom DataCard.
  - `numpy_data.py`: Example of creating a DataCard with NumPy data.
  - `pandas_data.py`: Example of creating a DataCard with a Pandas dataframe.
  - `polars_data.py`: Example of creating a DataCard with a Polars dataframe.
  
- `model/`: Contains examples of how to use Opsml to create ModelCards for various machine learning models.
  - `catboost_model.py`: Example of creating a ModelCard for a CatBoost model.
  - `custom_model.py`: Example of creating a custom ModelCard.
  - `hf_model.py`: Example of creating a ModelCard for a Hugging Face model.
  - `lightgbm_model.py`: Example of creating a ModelCard for a LightGBM model.
  - `lightning_model.py`: Example of creating a ModelCard for a Lightning AI model.
  - `onnx_model.py`: Example of creating a ModelCard for an ONNX model.
  - `sklearn_model.py`: Example of creating a ModelCard for a Scikit-learn model.
  - `tensorflow_model.py`: Example of creating a ModelCard for a TensorFlow model.
  - `torch_model.py`: Example of creating a ModelCard for a PyTorch model.
  - `xgb_booster.py`: Example of creating a ModelCard for an XGBoost model.

- `llm/`: Contains examples of how to use Opsml with various LLM frameworks.
  - `chat/`: Directory containing examples for making chat completion calls with various sdks.
    - `openai_chat.py`: Example of using Opsml with the OpenAI SDK for chat completions.
    - `openai_responses.py`: Example of using Opsml with the OpenAI SDK for the responses API.
    - `pydantic_chat.py`: Example of using Opsml with the Pydantic AI framework for chat completions.
  - `google_adk/`: FastAPI app that shows how to use Opsml with the Google ADK framework to create a multi-step agent.
  - `pydantic/`: FastAPI app that shows how to use Opsml with the Pydantic AI framework to create a multi-step agent.

- `experiment/`: Contains examples of how to use Opsml for experiment tracking and management.
  - `basic.py`: Example of using Opsml for basic experiment tracking with Sklearn
  - `advanced.py`: Example of using Opsml for advanced experiment tracking with PyTorch and logging parameters, metrics and artifacts.
  
- `api/`: Contains examples of how to use Opsml with FastAPI to create APIs.