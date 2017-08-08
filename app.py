# -*- coding: utf-8 -*-
"""resin.io in production

A Flask app to show resin.io project tags that are deployed.

Required environment variables:

* `REPO_LIST`: semicolon serparated list of repos to monitor,
  for example `resin-io/resin-admin:resin-io/resin-ui`
* `GITHUB_TOKEN`: a valid GitHub token that can read all the requested repos
* `SECRET`: just an app secret, something random
"""
import os
from flask import Flask, render_template, flash
from github import Github
APP = Flask(__name__)

def parse_repolist():
    """Parse watched repos from the `REPO_LIST` env var.
    """
    repolist_env = os.environ.get('REPO_LIST', None)
    repolist = []
    if repolist_env:
        for repo in repolist_env.split(':'):
            repolist += [{'full_name': repo}]
    return repolist

def get_repo_info(repo_full_name):
    """Get master and production information for a given repo.

    `repo_full_name`: the `owner/repo` format name of the repo to query
    """
    repo = GITHUB.get_repo(repo_full_name)
    master_branch = repo.get_branch('master')
    production_branch = repo.get_branch('production')
    thisrepo = {'repo_full_name': repo_full_name,
                'master_tags': [],
                'production_tags': [],
                'up_to_date': False}
    for tag in repo.get_tags():
        if tag.commit == master_branch.commit:
            thisrepo['master_tags'] += [tag]

        if tag.commit == production_branch.commit:
            thisrepo['production_tags'] += [tag]
    for tag in thisrepo['production_tags']:
        if tag in thisrepo['master_tags']:
            thisrepo['up_to_date'] = True
            break
    return thisrepo

def get_all_repo_info():
    """Prepare all required repo's info
    """
    all_repo_info = []
    for repo in WATCH_REPOS:
        all_repo_info += [get_repo_info(repo['full_name'])]
    return all_repo_info

@APP.route('/')
def homepage():
    """Render the repo information.
    """
    if not GITHUB_TOKEN:
        flash("GitHub token is not set up properly, nothing to show...")
        repoinfo = None
    else:
        repoinfo = get_all_repo_info()
    return render_template('repos.html', repoinfo=repoinfo)

# Setup
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
APP.secret_key = os.environ.get('SECRET', 'I haven\'t set the secret')
WATCH_REPOS = parse_repolist()
if GITHUB_TOKEN:
    GITHUB = Github(GITHUB_TOKEN)

if __name__ == '__main__':
    APP.run(debug=True, use_reloader=True)
