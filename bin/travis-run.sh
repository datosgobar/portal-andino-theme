#!/bin/sh

set -e

sudo -u postgres psql -c "CREATE DATABASE datastore_test WITH OWNER ckan_default;"
sudo -u postgres psql -c "CREATE USER datastore_default WITH PASSWORD 'pass';"
sed -i 's/@db/@localhost/g' /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini

cd ${TRAVIS_BUILD_DIR}/ckanext/gobar_theme/tests/
export CKAN_LIB=/var/lib/ckan
sudo mkdir -p ${CKAN_LIB}/theme_config/
sudo chmod -R 777 ${CKAN_LIB}
sudo echo "" > ${CKAN_LIB}/theme_config/test_settings.json
sudo echo "" > ${CKAN_LIB}/theme_config/datajson_cache_backup.json
echo "Current user: $(whoami)"
nosetests --nocapture --nologcapture --ckan --reset-db --with-pylons=/home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini
cd -