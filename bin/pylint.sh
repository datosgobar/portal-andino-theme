#!/usr/bin/env bash

. /usr/lib/ckan/default/bin/activate

cd /opt/theme
pylint ckanext/
