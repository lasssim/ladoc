#!/bin/sh

mike set-default $DEFAULT_BRANCH --allow-undefined

# Build the site
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
VERSION_NAME=$(echo $CURRENT_BRANCH | tr '/' '-')
mike deploy $VERSION_NAME --push

