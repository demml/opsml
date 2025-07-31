# Where's my package!?

The following example demonstrates how to leverage Opsml with the google adk in order to create a multi-process agent that:

- (1) receives a query from the user who is requesting an update on a specific shipment.
- (2) The agents parses the query and extracts the shipment ID if provided.
- (3) The agent then queries the shipment service to get the latest coordinates of the shipment.
- (4) The coordinates are then used to make a prediction about the estimated time of arrival (ETA) of the shipment.
- (5) The agent then responds to the user with the ETA of the shipment.