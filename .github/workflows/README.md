# Env variables:

* **GCP_CREDENTIALS**: The Google Cloud service account JSON credentials for deployment
* **GCP_FUNCTIONS_SERVICE_ACCOUTN**: The Google Cloud Service Account email address matching the above credential
* **GCP_PROJECT_ID**: The Google Cloud project
* **GH_TEST_TOKEN**: The personal access token for testing, (It's currently a personal access token set up on Yuan's account, should match the one in github_auth_flow/tests-conftest.py). Used only for Tests
* **GH_TEST_ID**: The GitHub ID of the user the GH_TEST_TOKEN belongs to
* **WEBHOOK_SECRET**: The Github webhook secret
* **WEB_API_KEY**: The Web API key that's part of Firebase credential, used for python to log into Auth. Used only for Tests