#!/bin/sh

set -e;

docker exec andino /opt/theme/bin/tests.sh
docker exec andino /opt/theme/bin/pylint.sh
