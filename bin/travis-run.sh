#!/bin/sh -e

sudo -u postgres psql -c "CREATE DATABASE datastore_test WITH OWNER ckan_default;"
sudo -u postgres psql -c "CREATE USER datastore_default WITH PASSWORD 'pass';"
sed -i 's/@db/@localhost/g' /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini

cd /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/
mkdir /var/lib/ckan/theme_config/
if [ -d /var/lib/ckan/theme_config/ ] ; then     echo "Se creó bien el directorio"; else     echo "No se pudo crear el directorio"; fi
nosetests --nocapture --nologcapture --ckan --reset-db --with-pylons=/home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini
cd -