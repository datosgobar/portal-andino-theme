#!/bin/sh

set -e;

docker exec andino /opt/theme/bin/local_tests.sh
docker exec andino /opt/theme/bin/pylint.sh
