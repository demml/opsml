"""HuggingFace Transformers model registration with OpsML."""

import opsml
import opsml.huggingface
from opsml import HuggingFaceTask, TaskType, start_experiment
from transformers import BertConfig, BertForSequenceClassification  # type: ignore

config = BertConfig(
    vocab_size=32,
    hidden_size=8,
    num_hidden_layers=1,
    num_attention_heads=1,
    intermediate_size=16,
)
model = BertForSequenceClassification(config)

with start_experiment(space="examples", name="huggingface-quickstart"):
    card = opsml.huggingface.log_model(
        model,
        name="bert-sequence-classifier",
        hf_task=HuggingFaceTask.TextClassification,
        task_type=TaskType.Classification,
    )
    opsml.log_metric("accuracy", 0.88)
    opsml.log_param("hidden_size", 8)

print(f"Registered ModelCard v{card.version} uid={card.uid}")

# --- equivalent explicit form (full control) ---
# from opsml import HuggingFaceModel, ModelCard
# with start_experiment(space="examples", name="huggingface-quickstart") as exp:
#     card = ModelCard(
#         space="examples",
#         name="bert-sequence-classifier",
#         interface=HuggingFaceModel(
#             model=model,
#             hf_task=HuggingFaceTask.TextClassification,
#             task_type=TaskType.Classification,
#         ),
#     )
#     exp.register_card(card)
