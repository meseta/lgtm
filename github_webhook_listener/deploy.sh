#!/usr/bin/env bash

if [[ -z "$WEBHOOK_SECRET" ]]; then
    echo "WEBHOOK_SECRET not set, run inside pipenv" 1>&2
    exit 1
fi

pipenv lock -r > app/requirements.txt
gcloud functions deploy github_webhook_listener \
    --entry-point github_webhook_listener \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=128MB \
    --source app \
    --set-env-vars=WEBHOOK_SECRET=$WEBHOOK_SECRET \
    --service-account=$SERVICE_ACCOUNT