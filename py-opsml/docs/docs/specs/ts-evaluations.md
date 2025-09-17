# Technical Component Specification: Evaluations

## Overview

The Evaluations component in OpsML is designed to facilitate the assessment and benchmarking of machine learning models and agentic systems. It provides a structured way to define, execute, and store evaluation results, enabling users to compare different models and workflows effectively. This component is crucial for maintaining high standards in model performance and ensuring that deployed systems meet the desired criteria.

## User Steps
1. **Define Evaluation Criteria**: A user will create and evaluation by leveraging either the evaluate_llm or experiment.llm.evaluate function. This will require the user to specify an array of LLMRecords and evaluation metrics using an LLMEvalMetric. An optional `EvaluationConfig` can also be provided to expand the evaluation to include an `Embedder`, `embedding_targets`, and options for computing similarity metrics, cluster analysis, and histogram visualizations.
2. **Execute Evaluation**: The user will run the evaluation, which will process the provided LLMRecords against the specified metrics and return a structured result.
3. **Store Results**: If the user specifies `log_results=True`, the evaluation results will be stored in the OpsML registry, allowing for future reference and comparison.
   1. The evaluation results will be stored in a new `opsml_evaluation` table in the database, which includes fields for `uid`, `created_at`, `app_env`, `name`, and `evaluation_type`.
   2. A call will be made to opsml to create a new `EvaluationRecord` object that will be logged in the registry.
   3. The response will return an encryption key that can be used to encrypt and upload the evaluation results to the artifact store.
   4. Subsequent calls to retrieve the evaluation results will require this encryption key to decrypt and access the stored data.