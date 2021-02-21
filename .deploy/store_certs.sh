#!/usr/bin/env sh
mkdir -p /tmp/certs
cat "$KAFKA_AUTH_CERT_FILE" > /tmp/certs/service.cert
cat "$KAFKA_AUTH_PKEY_FILE" > /tmp/certs/service.pkey
cat "$KAFKA_AUTH_CA_FILE" > /tmp/certs/ca.pem
