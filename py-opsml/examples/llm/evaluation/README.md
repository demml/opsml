# Overview

The llm/evaluation directory contains examples for evaluating inputs, responses, etc. from LLM applications. You can use these examples as a starting point for your own evaluations.


# Examples

## Evaluate.py

### **Scenario:** 

You have a real-time application that takes a user's input and reformulates it into a better structured question before sending it for additional processing. You are working offline, and want to evaluate how well the reformulation is working.

### **Evaluation Steps:**

1. Collect a set of original user inputs and their reformulated versions. This could be from a database, file, etc.
2. Create a list of `LLMEvalRecord` objects to hold the original and reformulated questions.
3. Create an `LLMEvalMetric` object that includes a customer reformulation prompt.
4. Use the `evaluate_llm` function from Opsml to assess the reformulated questions.
