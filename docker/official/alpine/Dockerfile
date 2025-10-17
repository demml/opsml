FROM alpine:latest

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PROJECT_HOME=opsml

# Create non-root user and group
RUN addgroup -S opsml && adduser -S -G opsml -h /app opsml

# Install required packages
RUN apk add --no-cache \
    bash \
    nginx \
    nodejs \
    npm \
    curl \
    tzdata \
    netcat-openbsd \
    ca-certificates \
  && rm -rf /var/cache/apk/*

ARG OPSML_SERVER_PORT=8080
ARG OPSML_SERVER_BINARY

# Copy built UI, server binary, NGINX config, and entrypoint script
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/ui/node_modules /app/ui/node_modules/
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/ui/build /app/ui/build/
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/opsml-server /usr/local/bin/opsml-server
COPY docker/official/extras/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/official/extras/entrypoint.sh /entrypoint.sh

# Set permissions and create directories
RUN mkdir -p /var/log/nginx /var/run \
  && chmod +x /entrypoint.sh \
  && chmod +x /usr/local/bin/opsml-server \
  && chown -R opsml:opsml /var/log/nginx /var/run

ENV OPSML_SERVER_PORT=${OPSML_SERVER_PORT}

WORKDIR /app

USER opsml

EXPOSE 8000

CMD ["/entrypoint.sh"]