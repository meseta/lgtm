#!/usr/bin/env bash

# This script is for manual deploying
pipenv lock -r > app/requirements.txt
gcloud functions deploy game_core \
    --entry-point game_core \
    --runtime python39 \
    --trigger-topic "core_loop" \
    --memory=128MB \
    --source app \
    --service-account=$SERVICE_ACCOUNT