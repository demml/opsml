from .utils import get_reformulation_dataframe, reformulation_evaluation_prompt
from opsml.experiment import evaluate_llm, LLMEvalMetric, LLMEvalRecord

if __name__ == "__main__":
    df = get_reformulation_dataframe()

    llm_records = []

    # convert df to records and iterate
    records = df.to_dict(orient="records")
    for record in records:
        llm_records.append(
            LLMEvalRecord(
                context={
                    "user_query": record["user_query"],
                    "reformulated_query": record["reformulated_query"],
                },
                id=record["id"],
            )
        )

    results = evaluate_llm(
        records=llm_records,
        metrics=[
            LLMEvalMetric(
                name="reformulation",
                prompt=reformulation_evaluation_prompt(),
            )
        ],
    )

    print(results)
