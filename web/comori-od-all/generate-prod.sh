#!/usr/bin/sh

echo "ELASTIC_USER=elastic" > .env-prod
echo "ELASTIC_PASSWORD=$(openssl rand -base64 12)" >> .env-prod