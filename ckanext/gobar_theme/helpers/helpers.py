#!coding=utf-8
import csv
import json
import logging
import subprocess
from urlparse import urljoin
from urlparse import urlparse

import ckan.lib.helpers as ckan_helpers
import ckan.logic as logic
from ckan.common import request

logger = logging.getLogger(__name__)


def remove_url_param(keys, value=None, replace=None, controller=None,
                     action=None, extras=None, alternative_url=None):
    if isinstance(keys, basestring):
        keys = [keys]
    else:
        keys = keys

    params_nopage = [(k, v) for k, v in request.params.items() if k != 'page']
    params = list(params_nopage)
    if value:
        params.remove((keys[0], value))
    else:
        for key in keys:
            _ = [params.remove((k, v)) for (k, v) in params[:] if k == key]
    if replace is not None:
        params.append((keys[0], replace))
    if alternative_url:
        return ckan_helpers._url_with_params(alternative_url, params)
    return ckan_helpers._create_url_with_params(params=params, controller=controller, action=action, extras=extras)


def cut_text(text, limit):
    if len(text) > limit:
        text, remaining = text[:limit], text[limit:]
        if ' ' in remaining:
            text += remaining.split(' ')[0]
        text += '...'
    return text


def cut_img_path(url):
    return urlparse(url).path


def url_join(base, url, *args):
    return urljoin(base, url, *args)


def json_loads(json_string):
    return json.loads(json_string)


def accepted_mime_types():
    return [
        'html',
        'json',
        'xml',
        'text',
        'csv',
        'xls',
        'api',
        'pdf',
        'zip',
        'rdf',
        'nquad',
        'ntriples',
        'turtle',
        'shp'
    ]


def package_resources(pkg_id):
    package = logic.get_action('package_show')({}, {'id': pkg_id})
    return package['resources']


def valid_length(data, max_length):
    return len(data) <= max_length


def capfirst(s):
    return s[0].upper() + s[1:]


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
    from markupsafe import Markup
    return Markup(json.dumps(field))


def get_current_terminal_username():
    return subprocess.check_output("whoami").strip()


def delete_column_from_csv_file(csv_path, column_name):
    with open(csv_path, 'rb') as source:
        rdr = csv.reader(source)
        first_row = next(rdr)
        column_position = None
        try:
            column_position = first_row.index(column_name)
        except ValueError:
            # No existe una columna con el nombre que llegó por parámetro -> se usará el csv tal y como está
            return
        source.seek(0)
        list_with_rows = []
        for r in rdr:
            list_with_rows.append(tuple((r[x] for x in range(len(r)) if x != column_position)))
    with open(csv_path, 'wb') as result:
        wtr = csv.writer(result)
        for r in list_with_rows:
            wtr.writerow(tuple(x for x in r))
