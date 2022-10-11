import os
from defaults import defaults
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import base64
import json
import sqlalchemy
from google.oauth2 import service_account
from functools import cached_property
from opsml_data.registy.base_table import SqlDataRegistrySchema


class GCPCredentials:
    def __init__(self, gcp_creds: str):
        base_64 = base64.b64decode(gcp_creds).decode("utf-8")
        self.key = json.loads(base_64)

    @cached_property
    def credentials(self):
        return service_account.Credentials.from_service_account_info(self.key)


creds = GCPCredentials(gcp_creds=defaults.GCP_CREDS)

# connect_with_connector initializes a connection pool for a
# Cloud SQL instance of MySQL using the Cloud SQL Python Connector.
def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = "spmt-data-science:us-central1:data-registry-mysql"  # e.g. 'project:region:instance'
    db_user = "fp-admin"  # e.g. 'my-db-user'
    db_pass = "fp-admin"  # e.g. 'my-db-password'
    db_name = "flight-plan-data-registry"

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    connector = Connector(
        ip_type=ip_type,
        credentials=creds.credentials,
    )

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    engine = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return engine


engine = connect_with_connector()

SqlDataRegistrySchema.__table__.create(bind=engine, checkfirst=True)
