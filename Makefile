PROJECT=opsml
PYTHON_VERSION=3.11.2
SOURCE_OBJECTS=opsml
FORMAT_OBJECTS=opsml tests examples
ACTIVE_PYTHON := "$$(python -c 'import sys; print(sys.version_info[0:2])')"

.PHONY: format.black
format.black:
	uv run black ${FORMAT_OBJECTS}

.PHONY: format.isort	
format.isort:
	uv run isort ${FORMAT_OBJECTS}

.PHONY: format.ruff
format.ruff:
	uv run ruff check --silent --fix --exit-zero ${FORMAT_OBJECTS}

.PHONY: format
format: format.isort format.ruff format.black

.PHONY: format.ci
lints.format_check:
	uv run black --check ${SOURCE_OBJECTS}

.PHONY: lints.ruff
lints.ruff:
	uv run ruff check ${SOURCE_OBJECTS}

.PHONY: lints.pylint
lints.pylint:
	uv run pylint --rcfile pyproject.toml ${SOURCE_OBJECTS}

.PHONY: lints.mypy
lints.mypy:
	uv run mypy ${SOURCE_OBJECTS}

.PHONY: lints.gitleaks
lints.gitleaks:
	uv run gitleaks detect --log-level debug -v
	uv run gitleaks protect --log-level debug -v

.PHONY: lints
lints: lints.format_check lints.ruff lints.pylint lints.mypy lints.gitleaks

.PHONY: lints.ci
lints.ci: lints.format_check lints.ruff lints.pylint lints.mypy

.PHONY: test
setup: setup.sysdeps setup.python setup.project

.PHONY: setup.project
setup.project:
	uv pip install ".[all]"

.PHONY: test.unit
test.unit:
	uv run pytest \
		-m "not large and not compat and not appsec" \
		--ignore tests/integration \
		--cov \
		--cov-fail-under=0 \
		--cov-report xml:./coverage.xml \
		--cov-report term \
		--junitxml=./results.xml


.PHONY: test.coverage
test.coverage:
	uv run pytest \
		-m "not large and not compat" \
		--ignore tests/integration \
		--cov \
		--cov-fail-under=0 \
		--cov-report xml:./coverage.xml \
		--cov-report term \
		--junitxml=./results.xml

.PHONY: test.integration.gcp
test.integration.gcp:
	uv run pytest tests/integration/gcp \
		--cov \
		--cov-fail-under=0 \
		--cov-report html:coverage \
		--cov-report term \
		--junitxml=./results.xml

.PHONY: test.integration.azure
test.integration.azure:
	uv run pytest tests/integration/azure \
		--cov \
		--cov-fail-under=0 \
		--cov-report html:coverage \
		--cov-report term \
		--junitxml=./results.xml

.PHONY: test.integration.aws
test.integration.aws:
	uv run pytest tests/integration/aws \
		--cov \
		--cov-fail-under=0 \
		--cov-report html:coverage \
		--cov-report term \
		--junitxml=./results.xml

.PHONY: test.unit.missing
test.unit.missing:
	uv run pytest \
		-m "not large and not integration" \
		--cov \
		--cov-fail-under=0 \
		--cov-report html:coverage \
		--cov-report term-missing \
		--junitxml=./results.xml

.PHONY: test.registry
test.registry:
	uv run python -m pytest tests/test_registry/test_registry.py

.PHONY: test.doc_examples
test.doc_examples:
	uv run pytest tests/test_docs

.PHONY: publish.docs
publish.docs:
	cd docs && uv run mkdocs gh-deploy --force

.PHONY: generate.docs
generate.docs:
	pip install pdoc
	pdoc \
	opsml/cards/base.py \
	opsml/cards/audit.py \
	opsml/cards/data.py \
	opsml/cards/model.py \
	opsml/cards/project.py \
	opsml/cards/run.py \
	opsml/data/splitter.py \
	opsml/data/interfaces/_arrow.py \
	opsml/data/interfaces/_base.py \
	opsml/data/interfaces/_image.py \
	opsml/data/interfaces/_numpy.py \
	opsml/data/interfaces/_pandas.py \
	opsml/data/interfaces/_polars.py \
	opsml/data/interfaces/_sql.py \
	opsml/data/interfaces/_text.py \
	opsml/data/interfaces/_torch.py \
	opsml/model/interfaces/base.py \
	opsml/model/interfaces/catboost_.py \
	opsml/model/interfaces/huggingface.py \
	opsml/model/interfaces/lgbm.py \
	opsml/model/interfaces/pytorch_lightning.py \
	opsml/model/interfaces/pytorch.py \
	opsml/model/interfaces/sklearn.py \
	opsml/model/interfaces/tf.py \
	opsml/model/interfaces/vowpal.py \
	opsml/model/interfaces/xgb.py \
	opsml/model/challenger.py \
	opsml/model/loader.py \
	opsml/profile/profile_data.py \
	opsml/projects/active_run.py \
	opsml/projects/project.py \
	opsml/registry/registry.py \
	opsml/registry/semver.py \
	opsml/settings/config.py \
	opsml/types/huggingface.py \
	-o ./docs/docs/api --docformat google
	pip uninstall pdoc -y

