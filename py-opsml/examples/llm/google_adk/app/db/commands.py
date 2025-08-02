import sqlite3
import random
from pathlib import Path
from pydantic import BaseModel
import numpy as np
from typing import Optional
from opsml.logging import RustyLogger, LogLevel, LoggingConfig

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Debug),
)

db_path = Path(__file__).parent / "shipment.db"
SHIPMENT_STATUSES = ["in-transit", "at-warehouse", "delivered"]
US_DESTINATIONS = [
    "New York",
    "Los Angeles",
    "Chicago",
    "Houston",
    "Phoenix",
    "Philadelphia",
    "San Antonio",
    "San Diego",
    "Dallas",
    "San Jose",
]


class ShipmentRecord(BaseModel):
    id: int
    x1: float
    x2: float
    y1: float
    y2: float
    status: str
    destination: str

    def to_numpy(self) -> np.ndarray:
        """
        Converts the ShipmentRecord to a NumPy array.

        Returns:
            np.ndarray: A NumPy array with shape (1,4) containing the coordinates.
        """
        return np.array([self.x1, self.x2, self.y1, self.y2]).reshape(1, 4)


def startup_db() -> None:
    """
    Initializes the shipment.db SQLite database and populates it with 10 records.

    Each record has:
        - id: int (primary key)
        - x1: float between 0 and 1
        - x2: float between 0 and 1
        - y1: float between 0 and 1
        - y2: float between 0 and 1
        - shipment_status: str
        - destination: str

    Examples:
        >>> startup_db()
    """

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipment (
            id INTEGER PRIMARY KEY,
            x1 REAL NOT NULL,
            x2 REAL NOT NULL,
            y1 REAL NOT NULL,
            y2 REAL NOT NULL,
            status TEXT NOT NULL,
            destination TEXT NOT NULL
        )
    """)

    # Clear existing records for idempotency
    cursor.execute("DELETE FROM shipment")

    for i in range(1, 11):
        x1 = random.uniform(0, 1)
        x2 = random.uniform(0, 1)
        y1 = random.uniform(0, 1)
        y2 = random.uniform(0, 1)
        status = random.choice(SHIPMENT_STATUSES)
        destination = random.choice(US_DESTINATIONS)
        cursor.execute(
            "INSERT INTO shipment (id, x1, x2, y1, y2, status, destination) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (i, x1, x2, y1, y2, status, destination),
        )

    conn.commit()
    conn.close()

    logger.info(f"Database initialized at {db_path} with 10 records.")


def get_shipment_by_id(shipment_id: int) -> Optional[ShipmentRecord]:
    """
    Retrieves a shipment record by its ID from the shipment.db SQLite database.

    Args:
        shipment_id (int): The ID of the shipment to retrieve.

    Returns:
        Optional[ShipmentCoordinates]: The shipment record as a ShipmentCoordinates object, or None if not found.

    Examples:
        >>> record = get_shipment_by_id(1)
        >>> if record:
        ...     print(record.x1, record.x2, record.y1, record.y2)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, x1, x2, y1, y2, status, destination FROM shipment WHERE id = ?",
        (shipment_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return ShipmentRecord(
            id=row[0],
            x1=row[1],
            x2=row[2],
            y1=row[3],
            y2=row[4],
            status=row[5],
            destination=row[6],
        )
    return None


def shutdown_db() -> None:
    """
    Deletes the shipment.db SQLite database file.

    Examples:
        >>> shutdown_db()
    """
    try:
        if db_path.exists():
            db_path.unlink()
            logger.info(f"Database file {db_path} deleted.")
        else:
            logger.info("No database file to delete.")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
