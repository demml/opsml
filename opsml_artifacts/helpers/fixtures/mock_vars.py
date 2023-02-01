import os

from google.auth import load_credentials_from_file

cred_path = os.path.join(os.path.dirname(__file__), "fake_gcp_creds.json")

creds, _ = load_credentials_from_file(cred_path)


mock_vars = {
    "gcp_project": "test",
    "gcs_bucket": "test",
    "gcp_region": "test",
    "app_env": "staging",
    "path": os.getcwd(),
    "snowflake_api_auth": "test",
    "snowflake_api_url": "test",
    "db_username": "test",
    "db_password": "test",
    "db_name": "test",
    "db_instance_name": "test",
    "gcp_creds": creds,
    "gcsfs_creds": creds,
}
