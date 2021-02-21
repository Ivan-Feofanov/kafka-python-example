#!/usr/bin/env sh
mkdir -p /tmp/certs
echo "$KAFKA_AUTH_CERT_FILE" > /tmp/certs/service.cert
echo "$KAFKA_AUTH_PKEY_FILE" > /tmp/certs/service.pkey
echo "$KAFKA_AUTH_CA_FILE" > /tmp/certs/ca.pem
