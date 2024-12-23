
.PHONY: format
format:
	cargo fmt

.PHONY: lint
lints:
	cargo clippy --workspace --all-targets -- -D warnings

.PHONY: test.aws
test.aws:
	cargo test aws -- --nocapture 

.PHONY: test.gcs
test.gcs:
	cargo test google -- --nocapture 

.PHONY: test.local
test.local:
	cargo test local -- --nocapture 
