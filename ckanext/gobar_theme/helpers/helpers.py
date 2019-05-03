#!coding=utf-8
import csv
import json
import ckan.logic as logic
from markupsafe import Markup


def package_resources(pkg_id):
    package = logic.get_action('package_show')({}, {'id': pkg_id})
    return package['resources']


def attributes_has_at_least_one(attr, resource_attributes):
    for attributes in resource_attributes:
        if attributes.get(attr, ''):
            return True
    return False


def portal_andino_version():
    from ckanext.gobar_theme.actions import _get_portal_andino_version
    version = _get_portal_andino_version()
    version = version['portal-andino'] or 'Desarrollo'

    version = version.replace('release-', '')  # Elimino el release-
    version = version[:15]  # me quedo con los primeros 15 caracteres

    return version


def jsondump(field=''):
    return Markup(json.dumps(field))


