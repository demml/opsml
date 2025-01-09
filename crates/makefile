.PHONY: test.storage.gcs.client
test.storage.gcs.client:
	cargo test -p opsml-storage test_gcs_storage_client -- --nocapture

.PHONY: test.storage.aws.client
test.storage.aws.client:
	cargo test -p opsml-storage test_aws_storage_client -- --nocapture

.PHONY: test.storage.azure.client
test.storage.azure.client:
	cargo test -p opsml-storage test_azure_storage_client  -- --nocapture

.PHONY: test.storage.local.client
test.storage.local.client:
	cargo test -p opsml-storage test_local_storage_client -- --nocapture

.PHONY: test.storage.gcs.server
test.storage.gcs.server:
	cargo test -p opsml-storage test_gcs_storage_server -- --nocapture

.PHONY: test.storage.aws.server
test.storage.aws.server:
	cargo test -p opsml-storage test_aws_storage_server -- --nocapture

.PHONY: test.storage.azure.server
test.storage.azure.server:
	cargo test -p opsml-storage test_azure_storage_server -- --nocapture

.PHONY: test.storage.local.server
test.storage.local.server:
	cargo test -p opsml-storage test_local_storage_server -- --nocapture --test-threads 1

.PHONY: lints
lints:
	cargo clippy --workspace --all-targets -- -D warnings

.PHONY: format
format:
	cargo fmt --all