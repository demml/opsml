PROJECT=poetry-template
PYTHON_VERSION=3.9.9
SOURCE_OBJECTS=opsml_data


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
	poetry run mypy --ignore-missing-imports ${SOURCE_OBJECTS}
lints.pylint:
	poetry run pylint --rcfile pyproject.toml  ${SOURCE_OBJECTS}
lints: lints.flake8 lints.pylint
lints.ci: lints.flake8.ci lints.pylint lints.format_check

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
		poetry run coverage run -m pytest \
        --cov=./ \
		--cov-config=.coveragerc \
        --cov-report=xml:coverage-report-unit-tests.xml \
        --junitxml=coverage-junit-unit-tests.xml \
        --cov-report term

publish:
	poetry config repositories.shipt-deploy https://artifactory.shipt.com/artifactory/api/pypi/pypi-local
	poetry publish --repository shipt-deploy --build