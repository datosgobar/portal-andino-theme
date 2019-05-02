#!coding=utf-8
import json
import csv
import logging
import os
import subprocess
from HTMLParser import HTMLParser
from datetime import time
from urlparse import urljoin
from urlparse import urlparse

import moment
from crontab import CronTab
from dateutil import parser, tz
from pydatajson.core import DataJson
from pylons import config as config
import ckan.lib.formatters as formatters
import ckan.lib.helpers as ckan_helpers
import ckan.logic as logic
import ckan.model as model
from ckan.common import request, c, _
from ckanext import constants
from ckanext.gobar_theme.theme_config import ThemeConfig
from ckanext.gobar_theme.utils.data_json_utils import get_data_json_contents

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


def organizations_with_packages():
    organizations = logic.get_action('organization_list')({}, {'all_fields': True})
    organizations_with_at_least_one_package = [
        organization for organization in organizations if organization['package_count'] > 0
    ]
    return len(organizations_with_at_least_one_package)


def get_pkg_extra(pkg, keyname):
    if 'extras' in pkg and pkg['extras']:
        for extra in pkg['extras']:
            if extra['key'] == keyname:
                return extra['value']
    return None


def all_descendants(organization_list):
    descendants = []
    for organization in organization_list:
        descendants.append(organization['name'])
        if 'children' in organization and organization['children']:
            descendants += all_descendants(organization['children'])
    return descendants


def get_theme_config(path=None, default=None):
    theme_config = ThemeConfig(constants.CONFIG_PATH)
    return theme_config.get(path, default)


def url_join(base, url, *args):
    return urljoin(base, url, *args)


def json_loads(json_string):
    return json.loads(json_string)


def license_options(_existing_license_id=None):
    # En lugar de retornar una lista de tuplas, como hace el código original de CKAN, retorno una lista de licencias
    # para soportar el uso del campo 'license_ids'
    register = model.Package.get_license_register()
    sorted_licenses = sorted(register.values(), key=lambda x: x.title)
    return sorted_licenses


def id_belongs_to_license(_id, _license):
    return _id == _license.id or (hasattr(_license, 'legacy_ids') and _id in _license.legacy_ids)


def get_license(_id):
    for _license in license_options():
        if id_belongs_to_license(_id, _license):
            return _license
    return None


def get_license_title(license_id):
    for _license in license_options():
        if id_belongs_to_license(license_id, _license):
            return _license.title
    return None


def update_frequencies(freq_id=None):
    frequencies = [
        ("R/PT1S", u"Continuamente actualizado"),
        ("R/PT1H", u"Cada hora"),
        ("R/P1D", u"Diariamente"),
        ("R/P0.33W", u"Tres veces a la semana"),
        ("R/P0.5W", u"Dos veces a la semana"),
        ("R/P3.5D", u"Cada media semana"),
        ("R/P1W", u"Semanalmente"),
        ("R/P0.33M", u"Tres veces por mes"),
        ("R/P0.5M", u"Cada 15 días"),
        ("R/P1M", u"Mensualmente"),
        ("R/P2M", u"Bimestralmente"),
        ("R/P3M", u"Trimestralmente"),
        ("R/P4M", u"Cuatrimestralmente"),
        ("R/P6M", u"Cada medio año"),
        ("R/P1Y", u"Anualmente"),
        ("R/P2Y", u"Cada dos años"),
        ("R/P3Y", u"Cada tres años"),
        ("R/P4Y", u"Cada cuatro años"),
        ("R/P10Y", u"Cada diez años"),
        ('eventual', u'Eventual')
    ]
    if freq_id is not None:
        filtered_freq = [freq for freq in frequencies if freq[0] == freq_id]
        if filtered_freq:
            return filtered_freq[0]
        return None
    return frequencies


def field_types(field_type_id=None):
    types = [
        ("string", u"Texto (string)"),
        ("integer", u"Número entero (integer)"),
        ("number", u"Número decimal (number)"),
        ("boolean", u"Verdadero/falso (boolean)"),
        ("time", u"Tiempo ISO-8601 (time)"),
        ("date", u"Fecha ISO-8601 (date)"),
        ("date-time", u"Fecha y hora ISO-8601 (date-time)"),
        ("object", u"JSON (object)"),
        ("geojson", u"GeoJSON (geojson)"),
        ("geo_point", u"GeoPoint (geo_point)"),
        ("array", u"Lista de valores en formato JSON (array)"),
        ("binary", u"Valor binario en base64 (binary)"),
        ("any", u"Otro (any)")
    ]

    if field_type_id:
        filtered_field_type = [t for t in types if t[0] == field_type_id]
        if filtered_field_type:
            return filtered_field_type[0]
        return None

    return types


def distribution_types(distribution_type_id=None):
    types = [
        ("file", u"Archivo de datos"),
        ("api", u"API"),
        ("code", u"Código"),
        ("documentation", u"Documentación")
    ]

    if distribution_type_id:
        filtered_distribution_type = [t for t in types if t[0] == distribution_type_id]
        if filtered_distribution_type:
            return filtered_distribution_type[0]
        return None

    return types


def special_field_types(special_field_type_id=None):
    types = [
        ("time_index", u"Índice de tiempo"),
    ]
    if special_field_type_id is not None:
        filtered_special_field_type = [_id for _id in types if _id[0] == special_field_type_id]
        if filtered_special_field_type:
            return filtered_special_field_type[0]
        return None
    return types


def type_is_numeric(field_type):
    return field_type in ['integer', 'number']


def render_ar_datetime(datetime_):
    datetime_ = ckan_helpers._datestamp_to_datetime(convert_iso_string_to_utc(datetime_))
    if not datetime_:
        return ''
    details = {
        'min': datetime_.minute,
        'hour': datetime_.hour,
        'day': datetime_.day,
        'year': datetime_.year,
        'month': formatters._MONTH_FUNCTIONS[datetime_.month - 1]().lower(),
        'timezone': datetime_.tzinfo.zone,
    }
    return _('{day} de {month} de {year}').format(**details)


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


def get_distribution_metadata(resource_id):
    # Se importa 'datajson_actions' en la función para evitar dependencias circulares con 'config_controller'
    json_dict = get_data_json_contents()
    html_parser = HTMLParser()
    json_dict = html_parser.unescape(json_dict)
    datajson = DataJson(json_dict)
    dist = datajson.get_distribution(resource_id)
    return dist


def is_distribution_local(distribution_metadata):
    ckan_site_url = config.get('ckan.site_url')
    try:
        accessURL = distribution_metadata.get('accessURL', '')
        return accessURL.startswith(ckan_site_url)
    except AttributeError:
        logger.error("Se intentó buscar información de un recurso que no figura en el data.json")
    return False


def get_extra_value(extras_list, field):
    for extra_field in extras_list:
        if extra_field['key'] == field:
            return extra_field['value']
    return None


def convert_iso_string_to_utc(date_string=''):
    if date_string is None:
        return ''
    try:
        date_time = parser.parse(date_string)
    except ValueError:
        # date_string es un string inválido o None
        return ''
    if date_time.time() == time(0):
        return date_string
    if date_time.tzinfo is not None:
        utc_date_time = date_time.astimezone(tz.tzutc())
    else:
        utc_date_time = date_time
    utc_date_time = utc_date_time.replace(tzinfo=None)
    return utc_date_time.isoformat()


def date_format_to_iso(date):
    if date:
        return moment.date(date, "%d/%m/%Y").isoformat()
    return date


def jsondump(field=''):
    from markupsafe import Markup
    return Markup(json.dumps(field))


def get_default_background_configuration():
    background_opacity = config.get('andino.background_opacity')
    return background_opacity


def get_gtm_code():
    return get_theme_config('google_tag_manager.container-id') or \
           config.get('ckan.google_tag_manager.gtm_container_id', '')


def get_current_url_for_resource(package_id, resource_id):
    return os.path.join(config.get('ckan.site_url'), 'dataset', package_id, 'resource', resource_id)


def get_package_organization(package_id):
    return logic.get_action('package_show')({}, {'id': package_id}).get('organization', {})


def store_object_data_excluded_from_datajson(object_dict_name, data_dict):
    '''
    :param object_dict_name: string con el tipo de la entidad que se está manejando (ej. groups, resources, etc)
    :param data_dict: diccionario que contiene el id del objeto a guardar y la información que necesitamos almacenar
        pero que no corresponde tener en el data.json (dict); debería poder utilizarse siempre de la misma manera,
        sin importar el tipo del objeto que se desee guardar
    :return: None
    '''
    theme_config = ThemeConfig(constants.CONFIG_PATH)
    data_dict_id = data_dict.get('id', {})
    if data_dict:
        data_dict.pop('id')

        config_item = theme_config.get(object_dict_name, {})
        config_item.update({data_dict_id: data_dict})
        ThemeConfig(constants.CONFIG_PATH).set(object_dict_name, config_item)
        return config_item[data_dict.get('id', data_dict_id)]
    return None


def get_resource_icon(resource):
    icon_url = resource.get('icon_url', None)
    if icon_url:
        return icon_url
    package_id = resource['package_id']
    id_to_search_with = '%s_%s_%s' % (
        get_package_organization(package_id).get('id', ''),
        resource['package_id'],
        resource['id']
    )
    resource_in_config = get_theme_config('resources', {}).get(id_to_search_with, None)
    if resource_in_config is not None:
        return resource_in_config.get('icon_url', None)
    return None


def get_andino_base_page():
    return config.get('andino.base_page', 'gobar_page.html')


def get_default_series_api_url():
    return config.get('seriestiempoarexplorer.default_series_api_uri', '')


def search_for_cron_jobs_and_remove(comment_to_search_for):
    # Buscamos y eliminamos los cron jobs que contengan el comment especificado por parámetro
    if comment_to_search_for:
        cron = CronTab(get_current_terminal_username())
        jobs_with_specified_comment = cron.find_comment(comment_to_search_for)
        cron.remove(jobs_with_specified_comment)
        cron.write()


def create_or_update_cron_job(command, hour, minute, comment=''):
    if comment:
        search_for_cron_jobs_and_remove(comment)
    cron = CronTab(get_current_terminal_username())
    job = cron.new(command=command, comment=comment)
    job.hour.on(hour)
    job.minute.on(minute)
    cron.write()


def get_current_terminal_username():
    return subprocess.check_output("whoami").strip()


def search_for_value_in_config_file(field):
    # Solamente queremos utilizar el valor default cuando no existe uno ingresado por el usuario.
    try:
        value = subprocess.check_output(
            'grep -E "^{}[[:space:]]*=[[:space:]]*" '
            '/etc/ckan/default/production.ini | tr -d [[:space:]]'.format(field), shell=True).strip()
        return value.replace(field, '')[1:]
    except Exception:
        return ''


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


def prepare_context_variable():
    return {'model': model, 'session': model.Session,
            'user': c.user or c.author, 'for_view': True,
            'auth_user_obj': c.userobj}


def is_plugin_present(plugin_name):
    plugins = config.get('ckan.plugins')
    return plugin_name in plugins


def get_distribution_id():
    return get_data_json_contents().get('identifier') or ''
