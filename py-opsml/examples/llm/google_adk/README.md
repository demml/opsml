# Where's my package!?

The following example demonstrates how to leverage Opsml with the google adk in order to create a multi-process agent that:

- (1) receives a query from the user who is requesting an update on a specific shipment.
- (2) The agents parses the query and extracts the shipment ID if provided.
- (3) The agent then queries the shipment service to get the latest coordinates of the shipment.
- (4) The coordinates are then used to make a prediction about the estimated time of arrival (ETA) of the shipment.
- (5) The agent then responds to the user with the ETA of the shipment.


Setup:
- All steps assume you are running code from the `google_adk` directory.
  
1. Execute the following command to create the model and prompts (we're using uv):
   - This will create 1 ModelCard, 2 PromptCard, and a ServiceCard that combines groups the cards.
   - All cards will be registered in the Opsml Registry and are configured with monitoring.
```bash
uv run python -m app.train
```

2. Download the ServiceCard and artifacts from the Opsml Registry to a directory called `app/service_artifacts`:
   - This will download the service card and all artifacts required to run the service.
   - The service card is configured to use the model and prompts created in step 1.
```bash
uv run opsml get service --space opsml --name "shipment_service" --write-dir "app/service_artifacts"
```