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

setup.project.numpy1:
	uv sync --all-extras --group dev --group numpy1
	uv run maturin develop --features server


test.unit.numpy1: setup.project.numpy1
	uv run pytest \
		--ignore="tests/interfaces/model/test_tensorflow.py" \
		-m "numpy" \
		--cov \
		--cov-fail-under=0 \
		--cov-report xml:./coverage.xml \
		--cov-report term \

test.unit.tensorflow:
	uv run python tests/interfaces/model/test_tensorflow.py

test.unit:
	uv run pytest \
		--ignore="tests/genai/integration/*" \
		--ignore="tests/interfaces/model/test_tensorflow.py" \
		-m "not numpy" \
		--cov \
		--cov-fail-under=0 \
		--cov-report xml:./coverage.xml \
		--cov-report term 

setup.integration:
	uv sync --all-extras --group dev,docs
	uv run maturin develop --release 

test.integration:
	uv run pytest -s tests/integration

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

publish.docs:
	uv run mkdocs gh-deploy --force