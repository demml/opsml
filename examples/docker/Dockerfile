# Any extra packages to install can go here
ARG EXTRA_SYS_PACKAGES="\
  libpq-dev \
  "

ARG POETRY_VERSION=1.6.1
ARG PROJECT_NAME=opsml-api
ARG PY_VER_FULL=3.10.13
ARG PY_VER_MAJOR=3.10
ARG POETRY_VERSION=1.7.1
ARG PIPX_VERSION=1.2.0
ARG OPSML_STORAGE_URI
ARG OPSML_TRACKING_URI
ARG APP_ENV
ARG GOOGLE_ACCOUNT_JSON_BASE64

# required on all stages..e.g. CAs and timezones should never be stale
ARG SYS_PACKAGES="ca-certificates tzdata"

# Build python and poetry
FROM python:${PY_VER_FULL} AS python-pipx
ARG PIPX_VERSION
ENV PIPX_BIN_DIR=/usr/local/bin \
    PIPX_HOME=/opt/pipx

RUN mkdir --parents ${PIPX_HOME}

RUN wget https://github.com/pypa/pipx/releases/download/${PIPX_VERSION}/pipx.pyz \
    && python pipx.pyz install pipx \
    && rm pipx.pyz

FROM python-pipx as python-pipx-poetry
ARG POETRY_VERSION
ENV POETRY_VERSION=${POETRY_VERSION}

RUN pipx install poetry==${POETRY_VERSION}
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VIRTUALENVS_CREATE=true

FROM python-pipx-poetry as base
ARG EXTRA_SYS_PACKAGES
ARG PROJECT_NAME
ARG PY_VER_MAJOR
ARG SYS_PACKAGES

ENV PROJECT_HOME=/opt/${PROJECT_NAME}
ENV PROJECT_PYTHONPATH=${PROJECT_HOME}/.venv/lib/python${PY_VER_MAJOR}/site-packages
ENV PROJECT_VENV_BIN=${PROJECT_HOME}/.venv/bin

# prefix the venv bin to the path
ENV PATH=${PROJECT_VENV_BIN}${PATH:+":$PATH"}

RUN apt-get update --no-install-recommends \
  && apt-get install --no-install-recommends --yes \
  ${SYS_PACKAGES} \
  ${EXTRA_SYS_PACKAGES} \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get autoremove \
  && apt-get clean \
  && mkdir --parents ${PROJECT_VENV_BIN}  # also creates PROJECT_HOME

WORKDIR ${PROJECT_HOME}


# ================================================================
# Builder image
# adds python project files
# ================================================================
FROM base as builder

# separate caching layer for deps
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root

# caching layer for root
RUN poetry install --no-dev

# # ================================================================
# # Dev Image
# # adds testing and linting related files
# # ================================================================
FROM builder as dev

RUN poetry install

# # ================================================================
# # Prod Image
# # only module and venv related files
# # ================================================================
FROM python:${PY_VER_FULL}-slim as prod
ARG EXTRA_SYS_PACKAGES
ARG PROJECT_NAME
ARG PY_VER_MAJOR
ARG SYS_PACKAGES
ARG OPSML_STORAGE_URI
ARG OPSML_TRACKING_URI
ARG APP_ENV
ARG GOOGLE_ACCOUNT_JSON_BASE64

ENV OPSML_STORAGE_URI=${OPSML_STORAGE_URI}
ENV OPSML_TRACKING_URI=${OPSML_TRACKING_URI}
ENV APP_ENV=${APP_ENV}
ENV GOOGLE_ACCOUNT_JSON_BASE64=${GOOGLE_ACCOUNT_JSON_BASE64}
ENV PROJECT_HOME=/opt/${PROJECT_NAME}
ENV PROJECT_PYTHONPATH=${PROJECT_HOME}/.venv/lib/python${PY_VER_MAJOR}/site-packages
ENV PROJECT_VENV_BIN=${PROJECT_HOME}/.venv/bin

# prefix the venv bin to the path
ENV PATH=${PROJECT_VENV_BIN}${PATH:+":$PATH"}

RUN apt-get update --no-install-recommends \
  && apt-get install --no-install-recommends --yes \
  ${SYS_PACKAGES} \
  ${EXTRA_SYS_PACKAGES} \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get autoremove \
  && apt-get clean \
  && mkdir --parents ${PROJECT_VENV_BIN}  # also creates PROJECT_HOME

WORKDIR ${PROJECT_HOME}


COPY --from=builder ${PROJECT_PYTHONPATH} ${PROJECT_PYTHONPATH}
COPY --from=builder ${PROJECT_VENV_BIN} ${PROJECT_VENV_BIN}/


ENV PYTHONPATH=${PROJECT_PYTHONPATH}${PYTHONPATH:+":$PYTHONPATH"}
CMD gunicorn -k uvicorn.workers.UvicornWorker --workers=1 --bind=0.0.0.0:8000 "opsml.app.main:run_app()"