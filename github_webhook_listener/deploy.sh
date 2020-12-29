#!/usr/bin/env bash

pipenv lock -r > app/requirements.txt
gcloud functions deploy github_webhook_listener --entry-point github_webhook_listener --runtime python39 --trigger-http --allow-unauthenticated --memory=128MB --source app --set-env-vars=WEBHOOK_SECRET=$WEBHOOK_SECRET