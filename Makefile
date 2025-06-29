.PHONY: format
format:
	cargo fmt --all

.PHONY: lints
lints:
	cargo clippy --workspace --all-targets  -- -D warnings

lints.pedantic:
	cargo clippy --workspace --all-targets  -- -D warnings -W clippy::pedantic -A clippy::must_use_candidate -A clippy::missing_errors_doc

####### TOML tests
.PHONY: test.toml
test.toml:
	cargo test -p opsml-toml -- --nocapture --test-threads=1

####### CLI tests
.PHONY: test.cli
test.cli:
	cargo test -p opsml-cli -- --nocapture --test-threads=1

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
	cargo test -p opsml-storage test_local_storage_server -- --nocapture --test-threads 1

######## Collective Unit Tests
##.PHONY: test.unit
##test.unit: test.toml test.cli test.sql test.storage.server test.utils

######## Server tests

.PHONY: start.server
start.server: stop.server build.ui
	cargo build -p opsml-server
	./target/debug/opsml-server &


.PHONY: stop.server
stop.server:
	-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
#	rm -f opsml.db || true
#	rm -rf opsml_registries || true

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

.PHONY: test.version 
test.version:
	cargo test -p opsml-version -- --nocapture --test-threads=1

.PHONY: test.unit
test.unit: test.toml test.cli  test.sql test.storage.server test.server test.utils test.version test.cli

###### UI ######
UI_DIR = crates/opsml_server/opsml_ui
PY_DIR = py-opsml

ui.update.deps:
	cd $(UI_DIR) && pnpm update

.PHONY: ui.install.deps
install.ui.deps:
	cd $(UI_DIR) && pnpm install

.PHONY: ui.build
build.ui:
	cd $(UI_DIR) && pnpm install
	cd $(UI_DIR) && pnpm build
	touch $(UI_DIR)/site/.gitkeep # to make sure the site folder is not ignored by git

ui.dev:
	cd $(UI_DIR) && pnpm run dev

populate.cards:
	cd $(PY_DIR) && uv run python -m dev.populate_cards


.PHONY: changelog
prepend.changelog:
	# get version from Cargo.toml
	@VERSION=$(shell grep '^version =' Cargo.toml | cut -d '"' -f 2) && \
	git cliff --unreleased --tag $$VERSION --prepend CHANGELOG.md
