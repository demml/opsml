import json
import shutil
from pathlib import Path
from typing import List, Tuple

import torch
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from sklearn.model_selection import train_test_split
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizerFast,
    Trainer,
    TrainingArguments,
)

from examples.huggingface.create_dataset import TextWriterHelper
from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    HuggingFaceModel,
    HuggingFaceOnnxArgs,
    HuggingFaceORTModel,
    HuggingFaceTask,
    ModelCard,
    TextDataset,
)


class ExampleDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


class OpsmlHuggingFaceWorkflow:
    def __init__(self, info: CardInfo):
        """Instantiates workflow class. Instantiation will also set up the registries that
        will be used to store cards and artifacts

        Args:
            info:
                CardInfo data structure that contains required info for cards.
                You could also provide "name", "repository" and "email" to a card; however, this
                simplifies the process.

        """
        self.info = info
        self.registries = CardRegistries()

    def _create_datacard(self):
        """Shows how to create a data interface and datacard

        You can think of cards as outputs to each step in your workflow.
        In your data getting step, you will get your data, create a data interface,
        and then create/register a datacard, which will be stored in the registry.

        This example highlights the uses of the PandasData interface
        """

        data_interface = TextDataset(data_dir="examples/huggingface/data")

        # Create datacard
        datacard = DataCard(interface=data_interface, info=info)
        self.registries.data.register_card(card=datacard)

    def _get_data(self, dir_path: Path) -> Tuple[List[str], List[int]]:
        """Loads records in path and splits between text and labels"""

        texts = []
        labels = []
        for text_file in (dir_path).rglob("*.txt"):
            with open(text_file, "r") as f:
                record_str = f.read()
                record = json.loads(record_str)
                texts.append(record["text"])
                labels.append(record["label"])

        return texts, labels

    def _create_modelcard(self):
        """Shows how to create a model interface and modelcard

        This example highlights the uses of the HuggingFaceModel.
        """

        datacard: DataCard = self.registries.data.load_card(name=self.info.name)
        # No need to load the data since the image files are already in the correct directory

        # process data
        text, labels = self._get_data(Path("examples/huggingface/data"))
        train_texts, val_texts, train_labels, val_labels = train_test_split(text, labels, test_size=0.2)

        # get tokenizer
        tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

        train_encodings = tokenizer(train_texts, truncation=True, padding=True)
        val_encodings = tokenizer(val_texts, truncation=True, padding=True)

        train_dataset = ExampleDataset(train_encodings, train_labels)
        val_dataset = ExampleDataset(val_encodings, val_labels)

        training_args = TrainingArguments(
            output_dir="mlruns/results",
            num_train_epochs=1,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir="mlruns/logs",
            logging_steps=10,
        )

        model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )

        trainer.train()

        inputs = tokenizer(train_texts[0], return_tensors="pt", padding="max_length", truncation=True)

        interface = HuggingFaceModel(
            model=trainer.model,
            sample_data=inputs,
            tokenizer=tokenizer,
            task_type=HuggingFaceTask.TEXT_CLASSIFICATION.value,
            onnx_args=HuggingFaceOnnxArgs(
                ort_type=HuggingFaceORTModel.ORT_SEQUENCE_CLASSIFICATION.value,
                quantize=True,
                config=AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False),
            ),
        )

        # create modelcard
        modelcard = ModelCard(
            interface=interface,
            info=self.info,
            to_onnx=True,  # lets convert onnx
            datacard_uid=datacard.uid,  # modelcards must be associated with a datacard
        )
        self.registries.model.register_card(card=modelcard)

    def _test_onnx_model(self):
        """This shows how to load a modelcard and the associated model and onnx model (if converted to onnx)"""

        modelcard: ModelCard = self.registries.model.load_card(name=self.info.name)

        # load onnx model
        modelcard.load_onnx_model()
        inputs = dict(
            modelcard.preprocessor("This is a test", return_tensors="np", padding="max_length", truncation=True)
        )

        print(modelcard.onnx_model.sess(**inputs))

    def run_workflow(self):
        """Helper method for executing workflow"""
        self._create_datacard()
        self._create_modelcard()
        self._test_onnx_model()


if __name__ == "__main__":
    # populate data
    writer = TextWriterHelper()
    writer.generate_text_records()

    info = CardInfo(name="huggingface", repository="opsml", contact="user@email.com")
    workflow = OpsmlHuggingFaceWorkflow(info=info)
    workflow.run_workflow()

    # cleanup data
    shutil.rmtree(writer.write_path, ignore_errors=True)
