FROM rockylinux:9.3-minimal

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV PROJECT_HOME=opsml

RUN groupadd -r opsml && useradd -r -g opsml -s /bin/bash -d /app opsml

RUN microdnf update -y \
  && microdnf install -y \
    ca-certificates tzdata curl nginx nmap-ncat \
    glibc-langpack-en \
  && microdnf clean all \
  && rm -rf /var/cache/dnf/*

ARG OPSML_SERVER_PORT=8080
ARG OPSML_SERVER_BINARY

# Copy application files
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/ui/node_modules /app/ui/node_modules/
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/ui/build /app/ui/build/
COPY --chown=opsml:opsml ${OPSML_SERVER_BINARY}/opsml-server /usr/local/bin/opsml-server
COPY docker/official/extras/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/official/extras/entrypoint.sh /entrypoint.sh

RUN mkdir -p /var/log/nginx /var/run /var/lib/nginx \
  && rm -f /etc/nginx/conf.d/default.conf \
  && chmod +x /entrypoint.sh \
  && chmod +x /usr/local/bin/opsml-server \
  && chown -R opsml:opsml /var/log/nginx /var/run /var/lib/nginx

ENV OPSML_SERVER_PORT=${OPSML_SERVER_PORT}

WORKDIR /app

USER opsml

EXPOSE 8000

CMD ["/entrypoint.sh"]