import pandas as pd
import polars as pl
from opsml.evaluate import (
    EvaluationConfig,
    LLMEvalMetric,
    LLMEvalRecord,
    LLMEvalResults,
    evaluate_llm,
)
from opsml.experiment import start_experiment
from opsml.mock import OpsmlTestServer
from opsml.genai import Embedder, Provider
from opsml.genai.openai import OpenAIEmbeddingConfig
from opsml.mock import LLMTestServer
from tests.conftest import WINDOWS_EXCLUDE
import pytest


def test_llm_eval_no_embedding(
    reformulation_evaluation_prompt, relevancy_evaluation_prompt
) -> None:
    with LLMTestServer():
        records = []
        for i in range(10):
            record = LLMEvalRecord(
                context={"user_query": "my query", "response": "my response"},
                id=f"test_id_{i}",
            )
            records.append(record)

        reformulation_metric = LLMEvalMetric(
            name="reformulation",
            prompt=reformulation_evaluation_prompt,
        )
        relevancy_metric = LLMEvalMetric(
            name="relevancy",
            prompt=relevancy_evaluation_prompt,
        )
        results = evaluate_llm(
            records=records,
            metrics=[reformulation_metric, relevancy_metric],
        )

        metrics = results["test_id_1"].metrics

        assert metrics["reformulation"].score > 0
        assert metrics["relevancy"].score > 0

        result_df: pd.DataFrame = results.to_dataframe()

        assert isinstance(result_df, pd.DataFrame)

        result_polars_df: pl.DataFrame = results.to_dataframe(polars=True)

        assert isinstance(result_polars_df, pl.DataFrame)


def test_llm_eval_embedding(
    reformulation_evaluation_prompt, relevancy_evaluation_prompt
) -> None:
    with LLMTestServer():
        records = []

        embedder = Embedder(
            Provider.OpenAI,
            config=OpenAIEmbeddingConfig(
                model="text-embedding-3-small",
                dimensions=512,
            ),
        )
        for i in range(100):
            record = LLMEvalRecord(
                context={"user_query": "my query", "response": "my response"},
                id=f"test_id_{i}",
            )
            records.append(record)

        reformulation_metric = LLMEvalMetric(
            name="reformulation",
            prompt=reformulation_evaluation_prompt,
        )
        relevancy_metric = LLMEvalMetric(
            name="relevancy",
            prompt=relevancy_evaluation_prompt,
        )
        results = evaluate_llm(
            records=records,
            metrics=[reformulation_metric, relevancy_metric],
            config=EvaluationConfig(
                embedder=embedder,
                embedding_targets=["user_query", "response"],
                compute_similarity=True,
                cluster=True,
                compute_histograms=True,
            ),
        )
        metrics = results["test_id_1"].metrics

        assert metrics["reformulation"].score > 0
        assert metrics["relevancy"].score > 0

        result_df: pd.DataFrame = results.to_dataframe()

        assert isinstance(result_df, pd.DataFrame)

        result_polars_df: pl.DataFrame = results.to_dataframe(polars=True)

        assert isinstance(result_polars_df, pl.DataFrame)

        assert result_df.shape[0] == 100  # 10 records x 2 metrics

        # test model_dump_json and model_validate_json
        json_str = results.model_dump_json()
        assert isinstance(json_str, str)

        validated_results = results.model_validate_json(json_str)
        assert isinstance(validated_results, LLMEvalResults)

        histograms = results.histograms
        assert histograms is not None
        for field, histogram in histograms.items():
            print(f"Histogram for {field}: {histogram}")


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_experimentcard_evaluate_llm(
    reformulation_evaluation_prompt, relevancy_evaluation_prompt
):
    with OpsmlTestServer():
        with LLMTestServer():
            with start_experiment(space="test", log_hardware=True) as exp:
                records = []

                embedder = Embedder(
                    Provider.OpenAI,
                    config=OpenAIEmbeddingConfig(
                        model="text-embedding-3-small",
                        dimensions=512,
                    ),
                )
                for i in range(100):
                    record = LLMEvalRecord(
                        context={"user_query": "my query", "response": "my response"},
                        id=f"test_id_{i}",
                    )
                    records.append(record)

                reformulation_metric = LLMEvalMetric(
                    name="reformulation",
                    prompt=reformulation_evaluation_prompt,
                )
                relevancy_metric = LLMEvalMetric(
                    name="relevancy",
                    prompt=relevancy_evaluation_prompt,
                )

                results = exp.llm.evaluate(
                    records=records,
                    metrics=[reformulation_metric, relevancy_metric],
                    config=EvaluationConfig(
                        embedder=embedder,
                        embedding_targets=["user_query", "response"],
                        compute_similarity=True,
                        cluster=True,
                        compute_histograms=True,
                    ),
                )

                metrics = results["test_id_1"].metrics

                assert metrics["reformulation"].score > 0
                assert metrics["relevancy"].score > 0

                result_df: pd.DataFrame = results.to_dataframe()

                assert isinstance(result_df, pd.DataFrame)

                result_polars_df: pl.DataFrame = results.to_dataframe(polars=True)

                assert isinstance(result_polars_df, pl.DataFrame)
