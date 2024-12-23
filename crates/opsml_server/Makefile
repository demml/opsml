
.PHONY: format
format:
	cargo fmt

.PHONY: lint
lints:
	cargo clippy --workspace --all-targets -- -D warnings

.PHONY: test.file
test.file:
	cargo test file -- --nocapture 