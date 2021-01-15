#!/usr/bin/env bash

# For deploying manually

if [[ -z "$GCP_FUNCTIONS_SERVICE_ACCOUNT" ]]; then
    echo "GCP_FUNCTIONS_SERVICE_ACCOUNT not set, run inside pipenv" 1>&2
    exit 1
fi

# This script is for manual deploying
pipenv lock -r > app/requirements.txt
gcloud functions deploy create_new_game \
    --entry-point create_new_game \
    --runtime python39 \
    --trigger-topic "create_new_game" \
    --memory=128MB \
    --source app \
    --service-account=$GCP_FUNCTIONS_SERVICE_ACCOUNT
