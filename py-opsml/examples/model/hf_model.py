from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast  # type: ignore

from opsml.model import HuggingFaceTask, HuggingFaceModel, TaskType
from opsml.card import CardRegistry, RegistryType, ModelCard

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

# register ModelCard
model_registry.register_card(modelcard)

# list card
cards = model_registry.list_cards(uid=modelcard.uid).as_table()
