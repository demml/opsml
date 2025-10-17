FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PROJECT_HOME=opsml

RUN groupadd -r opsml && useradd -r -g opsml -s /bin/bash -d /app opsml

RUN apt-get update --no-install-recommends \
  && apt-get install --no-install-recommends --yes \
  ca-certificates tzdata curl nginx supervisor netcat-openbsd \
  && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
  && apt-get install --no-install-recommends --yes nodejs \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get autoremove \
  && apt-get clean

ARG OPSML_SERVER_PORT=8080
ARG OPSML_SERVER_BINARY

COPY ${OPSML_SERVER_BINARY}/opsml-server /usr/local/bin/opsml-server
COPY ${OPSML_SERVER_BINARY}/ui/build /app/ui/build/
COPY ${OPSML_SERVER_BINARY}/ui/node_modules /app/ui/node_modules/
COPY docker/official/ubuntu/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/official/ubuntu/entrypoint.sh /entrypoint.sh

# Set permissions and create directories
RUN mkdir -p /var/log/nginx /var/run \
  && rm -f /etc/nginx/sites-enabled/default \
  && chmod +x /entrypoint.sh \
  && chmod +x /usr/local/bin/opsml-server \
  && chown -R opsml:opsml /app \
  && chown -R opsml:opsml /var/log/nginx /var/run \
  && chown opsml:opsml /usr/local/bin/opsml-server

ENV OPSML_SERVER_PORT=${OPSML_SERVER_PORT}

# Switch to non-root user
USER opsml

EXPOSE 8000

CMD ["/entrypoint.sh"]