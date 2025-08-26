# Classification Service (Illustrates how to use OpsML with FastAPI)

The following example demonstrates how to leverage Opsml with FastAPI to create a classification service. 

Setup:
- All steps assume you are running code from the `api` directory.
- This API has model monitoring turned off by default. To enable it, make sure you have a Scouter server running and set the environment variable in your Opsml server. Uncomment all lines marked with "uncomment for model monitoring".
- Sklearn, Lightgbm, FastAPI, pandas and onnx must be installed (see associated requirement.txt)
  
1. Execute the following command to create 2 classification models packaged into a ServiceCard
   - 1 Random Forest Classifier
   - 1 LightGBM Classifier
   - Both models converted to onnx during ModelCard registration

```bash
uv run python -m app.train
```

1. Download the ServiceCard and artifacts from the Opsml Registry to a directory called `app/service_artifacts`:
   - This will download the service card and all artifacts required to run the service.
```bash
uv run opsml get service --space opsml --name "classification_service" --write-dir "app/service_artifacts"
```

1. Start the api using the following command:
   - This will start the api and make it available for the agent to query.
```bash
uv run uvicorn app.main:app --reload --port 8888
```

1. Make a request to the service:
   - This will return a response with both model predictions
   - 
```bash
curl -X POST "http://127.0.0.1:8888/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "feature_1": 1.0,
    "feature_2": 2.0,
    "feature_3": 3.0,
    "feature_4": 4.0,
    "feature_5": 5.0,
    "feature_6": 6.0,
    "feature_7": 7.0,
    "feature_8": 8.0,
    "feature_9": 9.0,
    "feature_10": 10.0
  }'
```