.PHONY: test.sql.sqlite
test.sql.sqlite:
	cargo test -p opsml-sql test_sqlite -- --nocapture --test-threads=1

.PHONY: test.sql.enum
test.sql.enum:
	cargo test -p opsml-sql test_enum -- --nocapture --test-threads=1

.PHONY: test.sql.postgres
test.sql.postgres:
	cargo test -p opsml-sql test_postgres -- --nocapture --test-threads=1

.PHONY: test.sql.mysql
test.sql.mysql:
	cargo test -p opsml-sql test_mysql -- --nocapture --test-threads=1

.PHONY: build.postgres
build.postgres:
	docker-compose down
	docker-compose up -d --build postgres

.PHONY: build.mysql
build.mysql:
	docker-compose down
	docker-compose up -d --build mysql

.PHONY: build
format:
	cargo fmt --all

.PHONY: lints
lints:
	cargo clippy --workspace --all-targets -- -D warnings

.PHONY: test.utils
test.utils:
	cargo test -p opsml-utils -- --nocapture

.PHONY: test.opsml.server
test.opsml.server:
	cargo test -p opsml-server test_opsml_server -- --nocapture --test-threads=1

.PHONY: test.opsml.registry.client
start.server:
	cargo build -p opsml-server
	./target/debug/opsml-server

.PHONY: test.opsml.registry.client
test.opsml.registry.client:
	cargo test --features server -p opsml-registry test_registry_client -- --nocapture --test-threads=1