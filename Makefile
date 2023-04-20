PROJECT=poetry-template
PYTHON_VERSION=3.9.16
SOURCE_OBJECTS=opsml


deploy.requirements:
	poetry export -f requirements.txt -o requirements.txt
	poetry export --dev -f requirements.txt -o requirements-dev.txt
deploy:
	poetry build

format.black:
	poetry run black ${SOURCE_OBJECTS}
format.isort:
	poetry run isort --atomic ${SOURCE_OBJECTS}
format: format.isort format.black

lints.format_check:
	poetry run black --check ${SOURCE_OBJECTS}
	poetry run isort --check-only ${SOURCE_OBJECTS}
lints.flake8:
	poetry run flake8 ${SOURCE_OBJECTS}
lints.flake8.ci:
	poetry run flake8 --output-file=flake8-output.txt ${SOURCE_OBJECTS}
lints.mypy:
	poetry run mypy ${SOURCE_OBJECTS}
lints.pylint:
	poetry run pylint --rcfile pyproject.toml  ${SOURCE_OBJECTS}
lints.ruff:
	poetry run ruff ${SOURCE_OBJECTS}
lints: lints.flake8 lints.pylint lints.ruff lints.mypy
lints.ci: lints.flake8.ci lints.pylint lints.ruff lints.format_check lints.mypy

setup: setup.python setup.sysdep.poetry setup.poetry-template
setup.unit:
	poetry install --all-extras --with dev
	poetry run install_integration --integration gcp
setup.quality:
	poetry install --all-extras --with dev,dev-lints
	poetry run install_integration --integration gcp
setup.uninstall:
	poetry env remove ${PYTHON_VERSION} || true
setup.ci: setup.ci.poetry setup.poetry-template
setup.ci.poetry:
	pip install poetry
setup.poetry-template:
	poetry install
setup.python:
	@test "$$(python -c 'import platform; print(platform.python_version())')" != "${PYTHON_VERSION}" \
        && echo ${PYTHON_VERSION} > .python-version || true
setup.sysdep.poetry:
	@command -v poetry \&> /dev/null \
		|| (echo "Poetry not found. \n  Installation instructions: https://python-poetry.org/docs/" \
		    && exit 1)

test.unit:
	poetry run pytest \
		--cov \
		--cov-fail-under=0 \
		--cov-report xml:./coverage.xml \
		--cov-report term \
		--junitxml=./results.xml

poetry.pre.patch:
	poetry version prepatch

poetry.sub.pre.tag:
	$(eval VER = $(shell grep "^version =" pyproject.toml | tr -d '"' | sed "s/^version = //"))
	$(eval TS = $(shell date +%s))
	$(eval REL_CANDIDATE = $(subst a0,rc.$(TS),$(VER)))
	@sed -i "s/$(VER)/$(REL_CANDIDATE)/" pyproject.toml

prep.pre.patch: poetry.pre.patch poetry.sub.pre.tag

publish:
	poetry config repositories.shipt-deploy https://artifactory.gcp.shipttech.com/artifactory/api/pypi/pypi-local
	poetry publish --repository shipt-deploy --build
