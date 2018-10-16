#!/bin/bash
set -e

echo "This is travis-build.bash..."

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install libcommons-fileupload-java

echo "Installing solt 4.7.2"
cd /opt
sudo wget http://archive.apache.org/dist/lucene/solr/4.7.2/solr-4.7.2.tgz
sudo tar -xvf solr-4.7.2.tgz
sudo cp -R solr-4.7.2/example /opt/solr
sudo mv /opt/solr/solr/collection1 /opt/solr/solr/ckan
echo "name=ckan" | sudo tee /opt/solr/solr/ckan/core.properties
sudo wget https://raw.githubusercontent.com/ckan/ckan/ckan-2.7.4/ckan/config/solr/schema.xml -O /opt/solr/solr/ckan/conf/schema.xml
sudo wget https://raw.githubusercontent.com/datosgobar/portal-base/master/solr/jetty-logging.xml -O /opt/solr/etc/jetty-logging.xml
echo "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_PORT=8983\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty
sudo java -jar /opt/solr/start.jar --daemon
cd -

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
export latest_ckan_release_branch='ckan-2.7.4'
echo "CKAN branch: $latest_ckan_release_branch"
git checkout $latest_ckan_release_branch
# Temporarily replace psycopg2's version with 2.7.1 which fixes https://github.com/psycopg/psycopg2/issues/594
sed -i.bak 's/psycopg2\=\=2\.4\.5/psycopg2\=\=2\.7\.1/' requirements.txt
python setup.py develop
pip install -r requirements.txt
# undo requirements.txt modification
git checkout requirements.txt
rm requirements.txt.bak
cd -

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Initialising the database..."
cd ckan
paster db init -c test-core.ini
cd -

git clone https://github.com/ckan/ckanext-googleanalytics
cd ckanext-googleanalytics
pip install -r requirements.txt
pip install --upgrade oauth2client
python setup.py develop
cd -

echo "Installing ckanext-gobar_theme and its requirements..."
python setup.py develop
pip install -r test-requirements.txt

echo "travis-build.bash is done."
