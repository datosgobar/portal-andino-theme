#!/bin/sh

set -e

sudo -u postgres psql -c "CREATE DATABASE datastore_test WITH OWNER ckan_default;"
sudo -u postgres psql -c "CREATE USER datastore_default WITH PASSWORD 'pass';"
sed -i 's/@db/@localhost/g' /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini

cd /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/
sudo mkdir /var/lib/ckan/
sudo mkdir /var/lib/ckan/theme_config/
sudo echo "" > /var/lib/ckan/theme_config/test_settings.json
sudo echo "" > /var/lib/ckan/theme_config/datajson_cache_backup.json
sudo chmod -R 777 /var/lib/
nosetests --nocapture --nologcapture --ckan --reset-db --with-pylons=/home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini
cd -