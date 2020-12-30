# For Developers

## Automatic Deployment
LGTM is deployed using [GitHub Actions](https://github.com/meseta/lgtm/actions) set up as CI/CD. Each Workflow's concern is one of the several microservices that make up LGTM, and should run Tests before deployment and as part of PRs. Workflows typically require secrets, such as service account credentials, or access tokens, for the deployment stages.

## Testing

Microservices should have tests that can be run using the `test` script (e.g. `pipenv run test` for python packages)

## Manual Deployment

Some microservices can be manually deployed by using the `deploy` script (e.g. `pipenv run deploy`). Relevant accounts should be set up (e.g. `gcloud` SDK or `firebase-cli`)