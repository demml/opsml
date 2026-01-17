###### The following script can be run to populate both Opsml and Scouter ######
# This script assumes you have already started both an Opsml server and Scouter server locally
# Refer to makefile targets dev.both.scouter
import os
from opsml._opsml import GenAIEvalProfile
from typing import Optional, cast

os.environ["OPSML_TRACKING_URI"] = "http://localhost:8090"
from opsml import (
    start_experiment,
    DataCard,
    ModelCard,
    PromptCard,
    ServiceCard,
    Card,
    RegistryType,
)
from opsml.model import ModelCardMetadata
from opsml.experiment import Experiment

from utils import (  # type: ignore
    create_chat_prompt,
    random_name,
    create_pandas_data,
    create_sklearn_interface,
    create_genai_tasks,
    SAVE_PATH,
    create_random_genaieval_record,
    create_random_features_record,
    create_random_metrics_record,
)
from opsml.scouter.tracing import (
    get_tracer,
    init_tracer,
    BatchConfig,
    get_current_active_span,
)
from opsml.scouter.transport import GrpcConfig
from opsml.scouter.drift import (
    GenAIEvalConfig,
)
from opsml.scouter.queue import ScouterQueue
import numpy as np

_GENAI_EVAL_PROFILE_PATH = SAVE_PATH / "genai_eval_profile.json"
_PSI_DRIFT_PROFILE_PATH = SAVE_PATH / "psi_drift_profile.json"
_CUSTOM_DRIFT_PROFILE_PATH = SAVE_PATH / "custom_drift_profile.json"


# Use Scouter Tracer
init_tracer(
    service_name="scouter-cards",
    transport_config=GrpcConfig(),
    batch_config=BatchConfig(scheduled_delay_ms=200),
)

tracer = get_tracer("scouter-cards")


class PopulateHelper:
    def __init__(self, name: Optional[str] = None, space: Optional[str] = None):
        self.name = name if name is not None else random_name()
        self.space = space if space is not None else random_name()

    @tracer.span("create_datacard")
    def create_datacard(self, exp: Experiment) -> DataCard:
        """Create and register a DataCard in the given experiment.

        Args:
            exp: The experiment to register the DataCard in.
        """
        datacard = DataCard(
            interface=create_pandas_data(),
            space=self.space,
            name=self.name,
            tags=["foo:bat", "baz:buz"],
        )

        exp.register_card(datacard)
        assert datacard.experimentcard_uid == exp.card.uid

        return datacard

    @tracer.span("create_modelcard")
    def create_modelcard(self, exp: Experiment, datacard: DataCard) -> ModelCard:
        """Create and register a ModelCard in the given experiment.

        Args:
            exp: The experiment to register the ModelCard in.
        """
        modelcard = ModelCard(
            interface=create_sklearn_interface(),
            space=self.space,
            name=self.name,
            tags=["foo:bar", "baz:qux"],
            metadata=ModelCardMetadata(
                datacard_uid=datacard.uid,
            ),
        )

        exp.register_card(modelcard)
        assert modelcard.experimentcard_uid == exp.card.uid

        # save the drift_profile to json
        modelcard.interface.drift_profile["psi"].save_to_json(_PSI_DRIFT_PROFILE_PATH)
        modelcard.interface.drift_profile["custom"].save_to_json(
            _CUSTOM_DRIFT_PROFILE_PATH
        )

        return modelcard

    @tracer.span("create_promptcard")
    def create_promptcard(self, exp: Experiment) -> PromptCard:
        """Create and register a PromptCard in the given experiment. This will also
        create and register an evaluation task for the prompt.

        Args:
            exp: The experiment to register the PromptCard in.
        """
        prompt_card = PromptCard(
            prompt=create_chat_prompt(),
            space=self.space,
            name=self.name,
            tags=["foo:bar", "baz:qux"],
        )

        prompt_card.create_eval_profile(
            alias="genai",
            config=GenAIEvalConfig(),
            tasks=create_genai_tasks(),
        )

        exp.register_card(prompt_card)
        assert prompt_card.experimentcard_uid == exp.card.uid

        profile = cast(GenAIEvalProfile, prompt_card.eval_profile["genai"])
        profile.save_to_json(_GENAI_EVAL_PROFILE_PATH)

        return prompt_card

    @tracer.span("log_experiment_artifacts")
    def log_experiment_artifacts(
        self,
        exp: Experiment,
        modelcard_uid: str,
        promptcard_uid: str,
    ):
        """Log artifacts to the experiment from the figure_dataset module."""
        for i in range(1, 11):  # Start from 1 to avoid log(0)
            exp.log_metric(
                name="step_metric",
                value=np.log(i) * 10,  # Scale by 10 for visibility
                step=i - 1,
            )

        initial_value = 100 * np.random.randint(1, 3)
        decay_rate = 0.05
        random_jitter = np.random.randint(0, 5)
        initial_value = initial_value + random_jitter

        exp.log_metric("score", 10)

        for i in range(0, 100):
            decay_value = initial_value * np.exp(-decay_rate * i)
            exp.log_metric(
                name="step_metric",
                value=decay_value,
                step=i,
            )

            exp.log_metric(name=f"mae_{i}", value=np.random.rand())
            exp.log_parameter(name=f"param_{i}", value=np.random.rand())
            exp.log_parameter(name=f"param2_{i}", value=np.random.rand())
            exp.log_parameter(name=f"param3_{i}", value="this is my param")

        deck = ServiceCard(
            space=self.space,
            name=self.name,
            cards=[
                Card(
                    alias="model",
                    uid=modelcard_uid,
                    registry_type=RegistryType.Model,
                ),
                Card(
                    alias="prompt",
                    uid=promptcard_uid,
                    registry_type=RegistryType.Prompt,
                ),
            ],
        )
        exp.register_card(deck)

    @tracer.span("setup_queue")
    def setup_queue(self):
        """Setup the Scouter queue with the saved drift and evaluation profiles.
        And attach it to the tracer.
        """
        queue = ScouterQueue.from_path(
            path={
                "psi": _PSI_DRIFT_PROFILE_PATH,
                "genai": _GENAI_EVAL_PROFILE_PATH,
                "custom": _CUSTOM_DRIFT_PROFILE_PATH,
            },
            transport_config=GrpcConfig(),
        )

        tracer.set_scouter_queue(queue)
        active_span = get_current_active_span()
        active_span.set_tag("scouter.queue", "setup_complete")

    def populate_queue(self):
        """Populate the Scouter queue with drift and evaluation profiles."""
        self.setup_queue()

        for i in range(0, 100):
            with tracer.start_as_current_span(f"genai_service_{i}") as active_span:
                active_span.set_tag("service.name", "genai-eval-service")
                record = create_random_genaieval_record()
                active_span.add_queue_item(alias="genai", item=record)

            with tracer.start_as_current_span(f"psi_service_{i}") as active_span:
                active_span.set_tag("service.name", "psi-drift-service")
                record = create_random_features_record()
                active_span.add_queue_item(alias="psi", item=record)

            with tracer.start_as_current_span(f"custom_service_{i}") as active_span:
                active_span.set_tag("service.name", "custom-drift-service")
                record = create_random_metrics_record()
                active_span.add_queue_item(alias="custom", item=record)

    def cleanup(self):
        """Cleanup any saved files."""
        if _GENAI_EVAL_PROFILE_PATH.exists():
            _GENAI_EVAL_PROFILE_PATH.unlink()
        if _PSI_DRIFT_PROFILE_PATH.exists():
            _PSI_DRIFT_PROFILE_PATH.unlink()
        if _CUSTOM_DRIFT_PROFILE_PATH.exists():
            _CUSTOM_DRIFT_PROFILE_PATH.unlink()

        # shutdown tracer
        tracer.shutdown()

    def populate(self):
        with tracer.start_as_current_span("experiment_loop"):
            with start_experiment(
                space=self.space, name=self.name, log_hardware=True
            ) as exp:
                # Create DataCard
                datacard = self.create_datacard(exp)

                # Create ModelCard and link it to DataCard
                modelcard = self.create_modelcard(exp, datacard)

                # Create PromptCard with evaluation tasks
                prompt_card = self.create_promptcard(exp)

                # Log artifacts to the experiment
                self.log_experiment_artifacts(
                    exp,
                    modelcard_uid=modelcard.uid,
                    promptcard_uid=prompt_card.uid,
                )

        # Populate the Scouter queue
        self.populate_queue()

        # Cleanup saved files
        self.cleanup()


if __name__ == "__main__":
    helper = PopulateHelper("scouter_populate", "scouter_dev")
    helper.populate()
