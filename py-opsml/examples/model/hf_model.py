import os

os.environ["OPSML_TRACKING_URI"] = "http://localhost:3000"

from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast  # type: ignore

from opsml.model import HuggingFaceTask, HuggingFaceModel, TaskType
from opsml.card import CardRegistry, RegistryType, ModelCard
from opsml.logging import RustyLogger, LoggingConfig, LogLevel


logger = RustyLogger.get_logger(
    config=LoggingConfig(log_level=LogLevel.Info),
)

logger.info("Starting the model card example...")
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")

# ... custom training code would go here...

model_registry = CardRegistry(registry_type=RegistryType.Model)

interface = HuggingFaceModel(
    model=model,
    tokenizer=tokenizer,
    hf_task=HuggingFaceTask.TextClassification,
    task_type=TaskType.Classification,
)

modelcard = ModelCard(interface=interface, space="opsml", name="my_model")

# logger.info("Registering the model card...")
model_registry.register_card(modelcard)

# logger.info("Listing the model card...")
cards = model_registry.list_cards(uid=modelcard.uid).as_table()

# logger.info("Loading the model card...")
loaded_modelcard = model_registry.load_card(uid=modelcard.uid)
