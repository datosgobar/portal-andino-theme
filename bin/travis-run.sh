#!/bin/sh -e

sudo -u postgres psql -c "CREATE DATABASE datastore_test WITH OWNER ckan_default;"
sudo -u postgres psql -c "CREATE USER datastore_default WITH PASSWORD 'pass';"
sed -i 's/@db/@localhost/g' /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini

cd /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/
sudo mkdir /var/
if [ -d /var/ ] ; then     echo "Se creó bien el directorio /var/"; else     echo "No se pudo crear el directorio /var/"; fi
sudo mkdir /var/lib/
if [ -d /var/lib/ ] ; then     echo "Se creó bien el directorio /var/lib/"; else     echo "No se pudo crear el directorio /var/lib/"; fi
sudo mkdir /var/lib/ckan/
if [ -d /var/lib/ckan/ ] ; then     echo "Se creó bien el directorio /var/lib/ckan/"; else     echo "No se pudo crear el directorio /var/lib/ckan/"; fi
sudo mkdir /var/lib/ckan/theme_config/
if [ -d /var/lib/ckan/theme_config/ ] ; then     echo "Se creó bien el directorio"; else     echo "No se pudo crear el directorio"; fi
nosetests --nocapture --nologcapture --ckan --reset-db --with-pylons=/home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini
cd -