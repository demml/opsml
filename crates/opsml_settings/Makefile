
.PHONY: format
format:
	cargo fmt

.PHONY: lint
lints:
	cargo clippy --workspace --all-targets -- -D warnings

.PHONY: test.unit
test.unit:
	cargo test -- --nocapture --test-threads=1 