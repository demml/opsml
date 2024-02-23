PROJECT=opsml
PYTHON_VERSION=3.11.2
SOURCE_OBJECTS=opsml
FORMAT_OBJECTS=opsml tests examples
ACTIVE_PYTHON := "$$(python -c 'import sys; print(sys.version_info[0:2])')"

format.black:
	poetry run black ${FORMAT_OBJECTS}
format.isort:
	poetry run isort ${FORMAT_OBJECTS}
format.ruff:
	poetry run ruff check --silent --fix --exit-zero ${FORMAT_OBJECTS}
format: format.isort format.ruff format.black

lints.format_check:
	poetry run black --check ${SOURCE_OBJECTS}
lints.ruff:
	poetry run ruff check ${SOURCE_OBJECTS}
lints.pylint:
	poetry run pylint --rcfile pyproject.toml ${SOURCE_OBJECTS}
lints.mypy:
	poetry run mypy ${SOURCE_OBJECTS}
lints.gitleaks:
	poetry run gitleaks detect --log-level debug -v
	poetry run gitleaks protect --log-level debug -v
lints: lints.format_check lints.ruff lints.pylint lints.mypy lints.gitleaks
lints.ci: lints.format_check lints.ruff lints.pylint lints.mypy

setup: setup.sysdeps setup.python setup.project
# setup.uninstall - handle in and out of project venvs
setup.uninstall:
	@export _venv_path=$$(poetry env info --path); \
    if [ ! -n "$${_venv_path:+1}" ]; then \
      echo "\nsetup.uninstall: didn't find a virtualenv to clean up"; \
      exit 0; \
    fi; \
    echo "\nattempting cleanup of $$_venv_path" \
    && export _venv_name=$$(basename $$_venv_path) \
    && ((poetry env remove $$_venv_name > /dev/null 2>&1 \
         || rm -rf ./.venv) && echo "all cleaned up!") \
    || (echo "\nsetup.uninstall: failed to remove the virtualenv." && exit 1)

setup.project:
	poetry install --all-extras --with dev,dev-lints

setup.python:
	@echo "Active Python version: $$(python --version)"
	@echo "Base Interpreter path: $$(python -c 'import sys; print(sys.executable)')"
	@export _python_version=$$(cat .tool-versions | grep -i python | cut -d' ' -f2) \
      && test "$$(python --version | cut -d' ' -f2)" = "$$_python_version" \
      || (echo "Please activate python version: $$_python_version" && exit 1)
	@poetry env use $$(python -c "import sys; print(sys.executable)")
	@echo "Active interpreter path: $$(poetry env info --path)/bin/python"
setup.sysdeps:
      # bootstrap python first to avoid issues with plugin installs that count on python
	@-asdf plugin-add python; asdf install python
	@asdf plugin update --all \
      && for p in $$(cut -d" " -f1 .tool-versions | sort | tr '\n' ' '); do \
           asdf plugin add $$p || true; \
         done \
      && asdf install \
      || (echo "WARNING: Failed to install sysdeps, hopefully things aligned with the .tool-versions file.." \
         && echo "   feel free to ignore when on drone")

test.unit:
	poetry run pytest \
		-m "not large and not compat" \
		--ignore tests/integration \
		--cov \
		--cov-fail-under=0 \
		--cov-report html:coverage \
		--cov-report term \
		--junitxml=./results.xml

test.integration:
	poetry run pytest tests/integration \
		--cov \
		--cov-fail-under=0 \
		--cov-report html:coverage \
		--cov-report term \
		--junitxml=./results.xml

test.unit.missing:
	poetry run pytest \
		-m "not large and not integration" \
		--cov \
		--cov-fail-under=0 \
		--cov-report html:coverage \
		--cov-report term-missing \
		--junitxml=./results.xml

test.registry:
	poetry run python -m pytest tests/test_registry/test_registry.py

test.doc_examples:
	poetry run pytest tests/test_docs

poetry.pre.patch:
	poetry version prepatch

poetry.sub.pre.tag:
	$(eval VER = $(shell grep "^version =" pyproject.toml | tr -d '"' | sed "s/^version = //"))
	$(eval TS = $(shell date +%s))
	$(eval REL_CANDIDATE = $(VER)-rc.$(TS))
	@sed -i "s/$(VER)/$(REL_CANDIDATE)/" pyproject.toml

prep.release.candidate : poetry.sub.pre.tag

publish:
	poetry publish --build

publish.docs:
	cd docs && poetry run mkdocs gh-deploy --force

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

