from opsml.mock import OpsmlTestServer, LLMTestServer
from opsml.experiment import LLMEvalRecord, LLMEvalMetric, evaluate_llm


def test_llm_eval(reformulation_evaluation_prompt, relevancy_evaluation_prompt) -> None:
    with OpsmlTestServer():
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

            for result in results:
                assert result["reformulation"].score > 0
                assert result["relevancy"].score > 0
