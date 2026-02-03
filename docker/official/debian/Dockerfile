FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PROJECT_HOME=opsml

# Create non-root user and group
RUN groupadd -r opsml && useradd -r -g opsml -s /bin/bash -d /app opsml

# Install required packages: nginx, nodejs, netcat, curl, etc.
RUN apt-get update --no-install-recommends \
  && apt-get install --no-install-recommends --yes \
     ca-certificates tzdata curl nginx netcat-openbsd gettext-base \
  && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
  && apt-get install --no-install-recommends --yes nodejs \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get autoremove \
  && apt-get clean

ARG NGINX_PORT=8000
ARG OPSML_SERVER_BINARY
ARG APP_ENV=staging

# Set environment variables
ENV NGINX_PORT=${NGINX_PORT}
ENV APP_ENV=${APP_ENV}

# Copy built UI, server binary, NGINX config, and entrypoint script
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/ui/node_modules /app/ui/node_modules/
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/ui/build /app/ui/build/
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/opsml-server /usr/local/bin/opsml-server
COPY --chown=opsml:opsml docker/official/extras/nginx/nginx.conf.template /etc/nginx/nginx.conf.template
COPY --chown=opsml:opsml docker/official/extras/entrypoint.sh /entrypoint.sh

# Set permissions and create directories
RUN chown -R opsml:opsml /etc/nginx \
  && mkdir -p /var/log/nginx /var/run /var/lib/nginx \
  && rm -f /etc/nginx/conf.d/default.conf \
  && chmod +x /entrypoint.sh \
  && chmod +x /usr/local/bin/opsml-server \
  && chown -R opsml:opsml /var/log/nginx /var/run /var/lib/nginx

WORKDIR /app

USER opsml

EXPOSE ${NGINX_PORT}

CMD ["/entrypoint.sh"]