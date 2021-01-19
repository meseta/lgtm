# Game Core Functions

* create_new_game: starts a new game and initial quest
* github_auth_flow: Completes auth from frontend for GitHub Oauth
* github_webhook_listener: Listens to forks from github

## Local Development

This package uses pipenv to manage python dependencies, to use, ensure `pipenv` is installed (`pip install pipenv`) and run the following to set up a local development:

```
pipenv install --dev
```

Edit .env (copy `sample.env` -> `.env`) appropriately.

## Useful commands

* `pypenv run serve <target name>` runs a test server of the target function
* `pipenv run pylint app` runs pylint across app folder
* `pipenv run mypy .` runs mypy (static typecheck) across this folder
* `pipenv run black .` runs Black autoformatter across this folder
* `pipenv run test` Runs all defined tests with pytest
