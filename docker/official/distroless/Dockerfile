FROM debian:bullseye-slim as certs
RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

FROM gcr.io/distroless/cc-debian11
COPY --from=certs /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

ARG OPSML_SERVER_BINARY

COPY ${OPSML_SERVER_BINARY} /opsml-server
USER nonroot:nonroot
ENTRYPOINT ["/opsml-server"]