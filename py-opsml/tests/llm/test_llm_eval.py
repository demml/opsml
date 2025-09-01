from opsml.mock import OpsmlTestServer, LLMTestServer
from opsml.experiment import LLMEvalRecord, LLMEvalMetric, evaluate_llm


def test_llm_eval(reformulation_evaluation_prompt) -> None:
    with OpsmlTestServer():
        with LLMTestServer():
            records = []

            for i in range(10):
                record = LLMEvalRecord(
                    context={"user_query": "my query", "response": "my response"},
                    id=f"test_id_{i}",
                )
                records.append(record)

            metric = LLMEvalMetric(
                name="test_metric",
                prompt=reformulation_evaluation_prompt,
            )
            result = evaluate_llm(records, [metric])

            print(result)
