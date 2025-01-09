#!/bin/bash

# Set default values if environment variables are not set
: "${OPSML_STORAGE_URI:=default_storage_uri}"
: "${OPSML_SERVER_PORT:=3000}"
: "${TEST_NAME:=test_filesystemstorage_with_http_google}"

export OPSML_STORAGE_URI
export PORT=$OPSML_SERVER_PORT

# Start the opsml_server in the background
cargo run opsml_server