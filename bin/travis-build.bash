#!/bin/bash
set -e

echo "This is travis-build.bash..."

echo "Installing the packages that CKAN requires..."
# Añado el repo de Postgresql v9.5 + key
sudo su -c "echo deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main >> /etc/apt/sources.list.d/pgdg.list"
sudo wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
sudo apt-get update -qq
sudo apt-get install postgresql-$PGVERSION solr-jetty libcommons-fileupload-java

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
export latest_ckan_release_branch='release-v2.5.3'
echo "CKAN branch: $latest_ckan_release_branch"
git checkout $latest_ckan_release_branch
python setup.py develop
pip install -r requirements.txt --allow-all-external
pip install -r dev-requirements.txt --allow-all-external
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
python setup.py develop
cd -

echo "Installing ckanext-gobar_theme and its requirements..."
python setup.py develop
pip install -r dev-requirements.txt

echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "travis-build.bash is done."