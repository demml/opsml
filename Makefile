PROJECT=poetry-template
PYTHON_VERSION=3.9.9
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
# TODO autocommit the formatting only changes and add it rev to .git-blame-ignore-revs?
format: format.isort format.black

lints.format.check:
	poetry run black --check ${SOURCE_OBJECTS}
	poetry run isort --check-only ${SOURCE_OBJECTS}
lints.flake8:
	poetry run flake8 --ignore=DAR,E203,W503,F841 ${SOURCE_OBJECTS}
lints.flake8.strict:
	poetry run flake8 ${SOURCE_OBJECTS}
#lints.pylint:
#	poetry run pylint --rcfile pyproject.toml ${SOURCE_OBJECTS}
lints: lints.flake8 lints.format.check
lints.strict: lints.flake8.strict lints.format.check

publish:
	export POETRY_HTTP_BASIC_SHIPT_DEPLOY_USERNAME=${ARTIFACTORY_PYPI_USERNAME} \
		POETRY_HTTP_BASIC_SHIPT_DEPLOY_PASSWORD=${ARTIFACTORY_PYPI_PASSWORD} && \
	poetry config repositories. https://artifactory.shipt.com/artifactory/api/pypi/pypi-local && \
	poetry publish --repository  --build

setup: setup.python setup.sysdep.poetry setup.poetry-template
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

test:
	docker-compose up test
test.clean:
	docker-compose down
	-docker images -a | grep ${PROJECT} | awk '{print $3}' | xargs docker rmi
	-docker image prune -f
test.shell:
	docker-compose run test /bin/bash
test.shell.debug:
	docker-compose run --entrypoint /bin/bash test
test.unit: setup
		poetry run pytest \
			--cov \
			--cov-fail-under=0 \
			--cov-report \
			xml:./coverage.xml \
			--junitxml=./results.xml