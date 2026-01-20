from typing import Any, Dict

from opsml.app import AppState
from opsml.card import ModelCard
from opsml.scouter import Features
from opsml.scouter.tracing import Tracer

from ..db.commands import ShipmentRecord, get_shipment_by_id


def build_tools(tracer: Tracer, app_state: AppState) -> Any:
    modelcard: ModelCard = app_state.service["eta"]
    # queue = app_state.queue["eta_metrics"]

    def get_shipment_eta_by_id(shipment_id: int) -> Dict[str, float | str | int]:
        """
        Retrieves the estimated delivery time for a shipment by its ID.

        Args:
            shipment_id (int): The ID of the shipment to retrieve.

        Returns:
            str: A string containing the estimated delivery time in hours.
        """

        with tracer.start_as_current_span(name="get_shipment_eta_by_id") as span:
            record: ShipmentRecord | None = get_shipment_by_id(shipment_id)

            if record is None:
                return {"error": f"Shipment with ID {shipment_id} not found."}

            # Simulate a model call to get the estimated delivery time
            eta = modelcard.model.predict(record.to_numpy())[0]

            # Log eta prediction
            span.add_queue_item(
                alias="eta_metrics",
                item=Features(features={**record.model_dump(), "target": eta}),
            )

            return {
                "eta": eta,
                "shipment_id": record.id,
                "status": record.status,
                "destination": record.destination,
            }

    return get_shipment_eta_by_id
