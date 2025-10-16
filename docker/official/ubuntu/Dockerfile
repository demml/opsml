FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PROJECT_HOME=opsml

RUN apt-get update --no-install-recommends \
  && apt-get install --no-install-recommends --yes \
  ca-certificates tzdata curl nginx supervisor \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install --no-install-recommends --yes nodejs \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get autoremove \
  && apt-get clean


ARG OPSML_SERVER_PORT=8080

# Copy rust binary
ARG OPSML_SERVER_BINARY
COPY ${OPSML_SERVER_BINARY} /usr/local/bin/opsml-server
RUN chmod +x /usr/local/bin/opsml-server

# Copy UI build (ui and node_modules)
COPY ${OPSML_SERVER_BINARY}/ui/build /app/ui
COPY ${OPSML_SERVER_BINARY}/ui/node_modules /app/ui/node_modules


# Copy nginx configuration
COPY docker/official/ubuntu/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY docker/official/ubuntu/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories and enable nginx site
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/run \
  && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default \
  && rm -f /etc/nginx/sites-enabled/default


ENV OPSML_SERVER_PORT=${OPSML_SERVER_PORT}

EXPOSE 80

# Start supervisor to manage both services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]