#!/bin/bash

helm repo add bitnami https://charts.bitnami.com/bitnami
helm template bitnami/redis -f values.yaml > redis.yaml
