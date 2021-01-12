#!/usr/bin/env bash

# For deploying manually

if [[ -z "$GCP_FUNCTIONS_SERVICE_ACCOUNT" ]]; then
    echo "GCP_FUNCTIONS_SERVICE_ACCOUNT not set, run inside pipenv" 1>&2
    exit 1
fi

pipenv lock -r > app/requirements.txt
gcloud functions deploy github_auth_flow \
    --entry-point github_auth_flow \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=128MB \
    --source app \
    --set-env-vars=WEB_API_KEY=$WEB_API_KEY \
    --service-account=$GCP_FUNCTIONS_SERVICE_ACCOUNT