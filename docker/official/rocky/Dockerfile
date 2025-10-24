FROM rockylinux:9-minimal

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PROJECT_HOME=opsml

RUN groupadd -r opsml && useradd -r -g opsml -s /bin/bash -d /app opsml

RUN microdnf update -y \
  && microdnf install -y \
    ca-certificates tzdata curl nginx nmap-ncat \
    glibc-langpack-en \
  && curl -fsSL https://rpm.nodesource.com/setup_22.x | bash - \
  && microdnf install -y nodejs \
  && microdnf clean all \
  && rm -rf /var/cache/dnf/*

ARG OPSML_PORT=8000
ARG OPSML_SERVER_BINARY

# Set environment variables
ENV OPSML_PORT=${OPSML_PORT}

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

EXPOSE ${OPSML_PORT}

CMD ["/entrypoint.sh"]