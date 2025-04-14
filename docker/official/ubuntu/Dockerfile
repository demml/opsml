FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PROJECT_HOME=opsml

RUN apt-get update --no-install-recommends \
  && apt-get install --no-install-recommends --yes \
  ca-certificates tzdata curl \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get autoremove \
  && apt-get clean

ARG OPSML_SERVER_BINARY

COPY ${OPSML_SERVER_BINARY} /opsml-server

CMD ["/opsml-server"]
