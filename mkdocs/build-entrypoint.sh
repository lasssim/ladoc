#!/bin/sh

set -e
set -x

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
VERSION_NAME=$(echo $CURRENT_BRANCH | tr '/' '-')

echo "Building site..."
echo
echo "  - Current directory: $(pwd)"
echo "  - DEFAULT_BRANCH: $DEFAULT_BRANCH"
echo "  - CURRENT_BRANCH: $CURRENT_BRANCH"
echo "  - DEPLOY_BRANCH: $DEPLOY_BRANCH"
echo "  - VERSION_NAME: $VERSION_NAME"
echo "  - GIT_COMMITTER_NAME: $GIT_COMMITTER_NAME"
echo "  - GIT_COMMITTER_EMAIL: $GIT_COMMITTER_EMAIL"
echo "  - GIT_URL_FROM: $GIT_URL_FROM"
echo "  - GIT_URL_TO: $GIT_URL_TO"
echo "  - DEPLOY_KEY: $DEPLOY_KEY"

mkdir -p /root/.ssh
echo $DEPLOY_KEY > /root/.ssh/id_rsa

# Convert HTTPS URL to SSH URL
GIT_URL_TO=$(echo $GIT_URL_TO | sed -E 's#https://([^:]+):([^@]+)@([^/]+)/(.*)#git@\3:\4#')
echo "  - GIT_URL_TO: $GIT_URL_TO"
#echo "  Changing git url to use CI_JOB_TOKEN..."
# Change the git url to use the CI_JOB_TOKEN
#git config --global url."$GIT_URL_TO".insteadOf "$GIT_URL_FROM" 
git remote set-url origin "$GIT_URL_TO"

echo "  Setting default branch to $DEFAULT_BRANCH..." 
mike set-default $DEFAULT_BRANCH --allow-undefined --branch $DEPLOY_BRANCH

echo "  Building site..."
# Build the site
mike deploy $VERSION_NAME --branch $DEPLOY_BRANCH

git push -v origin $DEPLOY_BRANCH

echo "  done."