""" The cast """

from typing import Optional, List, Union, Dict
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from functools import cached_property

from environs import Env
from google.cloud import secretmanager  # type: ignore
from github import Github, GithubException
from github.Issue import Issue
from github.Repository import Repository
from github.AuthenticatedUser import AuthenticatedUser
from github.GithubObject import NotSet, _NotSetType as NotSetType  # type: ignore

from .exceptions import CharacterError

env = Env()
GCP_PROJECT_ID = env("GCP_PROJECT_ID")

secret_client = secretmanager.SecretManagerServiceClient()


class ReactionType(Enum):
    """ Reaction types from https://docs.github.com/en/rest/reference/reactions#reaction-types """

    THUMBS_UP = "+1"
    THUMBS_DOWN = "-1"
    LAUGH = "laugh"
    CONFUSED = "confused"
    HEART = "heart"
    HOORAY = "hooray"
    ROCKET = "rocket"
    EYES = "eyes"


def fetch_secret(secret_name: str) -> str:
    secret_path = f"projects/{GCP_PROJECT_ID}/secrets/{secret_name}/versions/latest"
    secret = secret_client.access_secret_version(request=dict(name=secret_path))
    return secret.payload.data.decode()


class Character:
    def __init__(self, secret_name: str):
        self.token = fetch_secret(secret_name)
        self.github = Github(self.token)

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if hasattr(attr, "__call__"):

            def newfunc(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except GithubException as err:
                    raise CharacterError(f"Character error: {err}") from err

            return newfunc
        else:
            return attr

    @cached_property
    def user(self) -> AuthenticatedUser:
        """ Get user """
        return self.github.get_user()

    @property
    def user_id(self) -> int:
        """ Get own ID """
        return self.user.id

    @property
    def user_name(self) -> str:
        """ Get display name """
        return self.user.name

    def repo_get(self, repo: str) -> Repository:
        """ Get a repo, translating it's URL """
        repo_name = "/".join(repo.split("/")[-2:])
        return self.github.get_repo(repo)

    def issue_get(self, repo: str, issue_id: int) -> Issue:
        """ Get an issue """
        return self.repo_get(repo).get_issue(number=issue_id)

    def issue_create(self, repo: str, title: str, body: str) -> int:
        """ Post an issue in a repo, returns issue number """
        issue = self.github.get_repo(repo).create_issue(title=title, body=body)
        return issue.number

    def issue_close(self, repo: str, issue_id: int) -> None:
        """ Close an issue in a repo """
        issue = self.issue_get(repo, issue_id)
        issue.edit(state="closed")

    def issue_reaction_get_from_user(
        self, repo: str, issue_id: int, user_id: int
    ) -> List[ReactionType]:
        """ Get reactions on an issue's main post """
        issue = self.issue_get(repo, issue_id)
        reactions = issue.get_reactions()
        return [
            ReactionType(reaction.content)
            for reaction in reactions
            if reaction.user.id == user_id
        ]

    def issue_reaction_create(
        self, repo: str, issue_id: int, reaction: ReactionType
    ) -> None:
        """ Create a reaction on an issue """
        issue = self.issue_get(repo, issue_id)
        issue.create_reaction(reaction.value)

    def issue_comment_get_from_user_since(
        self, repo: str, issue_id: int, user_id: int, since: Union[datetime, NotSetType]
    ) -> Dict[int, str]:
        """ Get comment body text from a user on issue since date, presented as a dictionary with id:body """
        issue = self.issue_get(repo, issue_id)
        comments = issue.get_comments(since=since)
        return {
            comment.id: comment.body
            for comment in comments
            if comment.user.id == user_id
        }

    def issue_comment_get_from_user(
        self, repo: str, issue_id: int, user_id: int
    ) -> Dict[int, str]:
        """ Get comment body text from a user on issue """
        return self.issue_comment_get_from_user_since(repo, issue_id, user_id, NotSet)

    def issue_comment_create(self, repo: str, issue_id: int, body: str) -> int:
        """ Posts a comment, returning comment ID """
        issue = self.issue_get(repo, issue_id)
        comment = issue.create_comment(body)
        return comment.id

    def issue_comment_reaction_create(
        self, repo: str, issue_id: int, comment_id: int, reaction: ReactionType
    ) -> None:
        """ Set a reaction on a comment """
        issue = self.issue_get(repo, issue_id)
        comment = issue.get_comment(comment_id)
        comment.create_reaction(reaction.value)

    def issue_comment_reactions_get_from_user(
        self, repo: str, issue_id: int, comment_id: int, user_id: int
    ) -> List[ReactionType]:
        """ Get reactions for a particular coment from a user """
        issue = self.issue_get(repo, issue_id)
        comment = issue.get_comment(comment_id)
        reactions = comment.get_reactions()
        return [
            ReactionType(reaction.content)
            for reaction in reactions
            if reaction.user.id == user_id
        ]

    def issue_comment_delete(self, repo: str, issue_id: int, comment_id: int) -> None:
        """ Delete a comment """
        issue = self.issue_get(repo, issue_id)
        comment = issue.get_comment(comment_id)
        comment.delete()

    def __repr__(self) -> str:
        return f"Character(user_name={self.user_name})"


character_garry = Character("github_token_garry")
