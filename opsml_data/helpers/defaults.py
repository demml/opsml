from dataclasses import dataclass
import os


@dataclass
class Defaults:
    """Default kwargs that are passed to some operations,
    but can be overridden.
    """

    PATH = os.getcwd()
    GCS_BUCKET = os.getenv("GCS_BUCKET", "py-opsml")
    GCP_REGION = "us-central1"
    GCP_CREDS = os.getenv("GCP_CRED_BASE64")
    GCP_PROJECT = os.getenv("GCP_PROJECT")


defaults = Defaults()
