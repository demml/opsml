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
ARG OPSML_SERVER_BINARY

# Debug: List contents of the source directory
RUN echo "=== Debugging source directory ===" && \
    find ${OPSML_SERVER_BINARY} -type f -o -type d | sort || echo "Source directory not found"

# Copy rust binary with validation
COPY ${OPSML_SERVER_BINARY}/opsml-server /usr/local/bin/opsml-server
RUN chmod +x /usr/local/bin/opsml-server && \
    /usr/local/bin/opsml-server --version || echo "Binary validation failed"

# Create app directory structure
RUN mkdir -p /app/ui/build /app/ui/node_modules

# Copy UI build assets with proper error handling and fallbacks
COPY ${OPSML_SERVER_BINARY}/ui/build /app/ui/build/
RUN echo "UI build files copied:" && \
    find /app/ui/build -type f | head -10 || echo "No UI build files found"

# Copy node_modules (optional for production, mainly for development)
COPY ${OPSML_SERVER_BINARY}/ui/node_modules /app/ui/node_modules/
RUN echo "Node modules copied:" && \
    ls -la /app/ui/node_modules/ | head -10 || echo "No node_modules found"

# Copy configuration
COPY docker/official/ubuntu/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/official/ubuntu/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories and enable nginx site
RUN mkdir -p /var/log/supervisor /var/log/nginx /var/run \
  && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default \
  && rm -f /etc/nginx/sites-enabled/default

ENV OPSML_SERVER_PORT=${OPSML_SERVER_PORT}

EXPOSE 80

# Start supervisor to manage both services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]