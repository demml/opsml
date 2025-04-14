FROM rust:latest AS builder

RUN apt update && update-ca-certificates

FROM scratch

ARG OPSML_SERVER_BINARY

COPY ${OPSML_SERVER_BINARY} /opsml-server

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt

CMD ["/opsml-server"]