#!/usr/bin/env bash

set -e;

. /usr/lib/ckan/default/bin/activate

cd /opt/theme
pip install -r test-requirements.txt

PGPASSWORD=my_database_pass psql -U my_database_user ckan -h db <<EOM
DROP DATABASE IF EXISTS datastore_test;
DROP DATABASE IF EXISTS ckan_test;
DROP ROLE IF EXISTS ckan_default;

CREATE ROLE ckan_default;
ALTER USER ckan_default WITH ENCRYPTED PASSWORD 'pass';
ALTER ROLE "ckan_default" WITH LOGIN;
CREATE DATABASE datastore_test WITH OWNER ckan_default;
CREATE DATABASE ckan_test WITH OWNER ckan_default;

DROP USER IF EXISTS datastore_default;
CREATE USER datastore_default WITH PASSWORD 'pass';
EOM

export CKAN_LIB=/var/lib/ckan
sudo mkdir -p ${CKAN_LIB}/theme_config/
sudo chmod -R 777 ${CKAN_LIB}
sudo echo "" > ${CKAN_LIB}/theme_config/test_settings.json
sudo echo "" > ${CKAN_LIB}/theme_config/datajson_cache_backup.json
echo "Current user: $(whoami)"

/usr/lib/ckan/default/bin/nosetests --nocapture --nologcapture --ckan --reset-db --with-pylons=/opt/theme/ckanext/gobar_theme/tests/tests_config/test-core.ini $1
