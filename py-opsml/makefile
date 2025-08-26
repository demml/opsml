PROJECT=opml-core
PYTHON_VERSION=3.12.8
SOURCE_OBJECTS=python/opsml

format.isort:
	uv run isort ${SOURCE_OBJECTS}
format.black:
	uv run black ${SOURCE_OBJECTS}
format.ruff:
	uv run ruff check --silent --exit-zero ${SOURCE_OBJECTS}
format: format.isort format.ruff format.black

lints.format_check:
	uv run black --check ${SOURCE_OBJECTS}
lints.ruff:
	uv run ruff check ${SOURCE_OBJECTS}
lints.mypy:
	uv run mypy ${SOURCE_OBJECTS}
lints.pylint:
	uv run pylint ${SOURCE_OBJECTS}
lints: lints.ruff lints.pylint lints.mypy
lints.ci: lints.format_check lints.ruff lints.pylint lints.mypy

setup.project:
	uv sync --all-extras --group dev --group docs
	uv run maturin develop --features server

setup.adk:
	uv sync --group dev --group docs
	uv pip install -r requirements/requirements.adk.txt
	uv run maturin develop --features server

test.unit.tensorflow: setup.project
	uv pip install -r requirements/requirements.tf.txt
	uv run pytest \
		--ignore="tests/interfaces/model/test_tensorflow.py" \
		-m "tensorflow" \
		--cov \
		--cov-fail-under=0 \
		--cov-report xml:./coverage.xml \
		--cov-report term
	uv run python tests/interfaces/model/test_tensorflow.py

test.unit:
	uv run pytest \
		--ignore="tests/genai/integration/*" \
		--ignore="tests/interfaces/model/test_tensorflow.py" \
		--ignore="tests/service" \
		-m "not tensorflow" \
		--cov \
		--cov-fail-under=0 \
		--cov-report xml:./coverage.xml \
		--cov-report term 

setup.integration:
	uv sync --all-extras --group dev,docs
	uv run maturin develop --release 

test.integration:
	uv run pytest -s tests/integration

test.service:
	uv run pytest -s tests/service

test.examples.data:
	uv run python examples/data/arrow_data.py && \
	uv run python examples/data/numpy_data.py && \
	uv run python examples/data/pandas_data.py && \
	uv run python examples/data/polars_data.py && \
	uv run python examples/data/custom_data.py

test.examples.model:
	uv pip install -r requirements/requirements.examples.txt
	uv run python examples/model/catboost_model.py && \
	uv run python examples/model/custom_model.py && \
	uv run python examples/model/hf_model.py && \
	uv run python examples/model/lightgbm_booster.py && \
	uv run python examples/model/lightning_model.py && \
	uv run python examples/model/onnx_model.py && \
	uv run python examples/model/sklearn_model.py && \
	uv run python examples/model/tensorflow_model.py && \
	uv run python examples/model/torch_model.py && \
	uv run python examples/model/xgb_booster.py

test.examples: test.examples.data test.examples.model

uv.pre.patch:
	uv version prepatch

uv.sub.pre.tag:
	$(eval VER = $(shell grep "^version =" pyproject.toml | tr -d '"' | sed "s/^version = //"))
	$(eval TS = $(shell date +%s))
	$(eval REL_CANDIDATE = $(subst a0,rc.$(TS),$(VER)))
	@sed -i "s/$(VER)/$(REL_CANDIDATE)/" pyproject.toml

prep.pre.patch: uv.pre.patch uv.sub.pre.tag

setup.docs:
	uv sync --all-extras --group docs
	uv run maturin develop --features server

build.docs:
	uv run mkdocs build

serve.docs:
	uv run python scripts/build_docs.py
	uv run mkdocs serve

publish.docs:
	uv run python scripts/build_docs.py
	uv run mkdocs gh-deploy --force

upgrade.deps:
	uv sync --upgrade --all-extras