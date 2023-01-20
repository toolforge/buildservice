#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

CURDIR=$PWD
HARBOR_DIR=".harbor"
HARBOR_VERSION=${HARBOR_VERSION:-v2.5.4}  # we use this for now

export HARBOR_HOSTNAME="${HARBOR_IP?"HARBOR_IP variable is not set"}"

[[ -e $HARBOR_DIR ]] || mkdir -p "$HARBOR_DIR"
cd "$HARBOR_DIR"
wget \
    https://github.com/goharbor/harbor/releases/download/"${HARBOR_VERSION}"/harbor-online-installer-"${HARBOR_VERSION}".tgz \
    -O harbor-"${HARBOR_VERSION}".tgz
tar xvzf  harbor-"${HARBOR_VERSION}".tgz
cd harbor
"$CURDIR"/utils/parse_harbor_config.py .
./prepare
# the above runs a docker container and changes permissions for the data dirs,
# so the containers have the correct ones, but that forces us to use sudo when
# using docker-compose

echo -e "Now you can start harbor by running"\
    "'sudo $(which docker-compose) -f $PWD/docker-compose.yml up -d', enjoy!" \
    "\nYou can also login into your new instance with user 'admin' and "\
    "password 'Harbor12345' on http://127.0.0.1"
