#!/bin/sh -e

sudo -u postgres psql -c "CREATE DATABASE datastore_test WITH OWNER ckan_default;"
sudo -u postgres psql -c "CREATE USER datastore_default WITH PASSWORD 'pass';"
echo "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_PORT=8983\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty
sed -i 's/@db/@localhost/g' /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini
sudo cp ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
diff -u ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sudo service jetty restart
echo "Jetty status"
sudo service jetty status
cd /home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/
nosetests --nocapture --nologcapture --ckan --reset-db --with-pylons=/home/travis/build/datosgobar/portal-andino-theme/ckanext/gobar_theme/tests/tests_config/test-core.ini
cd -