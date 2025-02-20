.PHONY: format
format:
	cargo fmt --all

.PHONY: lints
lints:
	cargo clippy --workspace --all-targets  -- -D warnings

lints.pedantic:
	cargo clippy --workspace --all-targets  -- -D warnings -W clippy::pedantic -A clippy::must_use_candidate -A clippy::missing_errors_doc

####### SQL tests
.PHONY: test.sql.sqlite
test.sql.sqlite:
	cargo test -p opsml-sql test_sqlite -- --nocapture --test-threads=1

.PHONY: test.sql.enum
test.sql.enum:
	cargo test -p opsml-sql test_enum -- --nocapture --test-threads=1

.PHONY: build.postgres
build.postgres:
	docker compose down
	docker compose up -d --build postgres --wait

.PHONY: test.sql.postgres
test.sql.postgres: build.postgres
	cargo test -p opsml-sql test_postgres -- --nocapture --test-threads=1
	docker compose down

.PHONY: build.mysql
build.mysql:
	docker compose down
	docker compose up -d --build mysql --wait

.PHONY: test.sql.mysql
test.sql.mysql: build.mysql
	cargo test -p opsml-sql test_mysql -- --nocapture --test-threads=1
	docker compose down

.PHONY: test.sql
test.sql: test.sql.sqlite test.sql.enum test.sql.postgres test.sql.mysql

######## Storage tests

.PHONY: test.storage.local.server
test.storage.local.server:
	cargo test --release -p opsml-storage test_local_storage_server -- --nocapture --test-threads 1

######## Server tests

.PHONE: build.server
build.server:
	cargo build -p opsml-server
	./target/debug/opsml-server &


.PHONE: stop.server
stop.server:
	lsof -ti:3000 | xargs kill -9

######## Storage tests
.PHONY: test.storage.client
test.storage.client:
	cargo test -p opsml-storage test_local_storage_client -- --nocapture

.PHONY: test.storage.server
test.storage.server:
	cargo test -p opsml-storage test_local_storage_server -- --nocapture --test-threads 1


.PHONY: test.utils
test.utils:
	cargo test -p opsml-utils -- --nocapture

.PHONY: test.opsml.server
test.server:
	cargo test -p opsml-server test_opsml_server -- --nocapture --test-threads=1

.PHONY: test.opsml.registry.client
test.opsml.registry.client:
	cargo test --features server -p opsml-registry test_registry_client -- --nocapture --test-threads=1
