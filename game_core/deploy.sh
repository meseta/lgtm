#!/usr/bin/env bash

# For deploying manually

if [[ -z "$GCP_FUNCTIONS_SERVICE_ACCOUNT" ]]; then
    echo "GCP_FUNCTIONS_SERVICE_ACCOUNT not set, run inside pipenv" 1>&2
    exit 1
fi

if [[ -z "$WEBHOOK_SECRET" ]]; then
    echo "WEBHOOK_SECRET not set, run inside pipenv" 1>&2
    exit 1
fi

if [[ -z "$WEB_API_KEY" ]]; then
    echo "WEB_API_KEY not set, run inside pipenv" 1>&2
    exit 1
fi

pipenv lock -r > app/requirements.txt

# Deploy github webhook listener
gcloud functions deploy github_webhook_listener \
    --entry-point github_webhook_listener \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=128MB \
    --source app \
    --set-env-vars=WEBHOOK_SECRET=$WEBHOOK_SECRET \
    --service-account=$GCP_FUNCTIONS_SERVICE_ACCOUNT

# Deploy github auth flow
gcloud functions deploy github_auth_flow \
    --entry-point github_auth_flow \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --memory=128MB \
    --source app \
    --set-env-vars=WEB_API_KEY=$WEB_API_KEY \
    --service-account=$GCP_FUNCTIONS_SERVICE_ACCOUNT

# Deploy tick
gcloud functions deploy tick \
    --entry-point tick \
    --runtime python39 \
    --trigger-event "providers/cloud.pubsub/eventTypes/topic.publish" \
    --trigger-resource "tick" \
    --memory=128MB \
    --source app \
    --service-account=$GCP_FUNCTIONS_SERVICE_ACCOUNT