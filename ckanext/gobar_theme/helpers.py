# coding=utf-8
from urlparse import urlparse
from HTMLParser import HTMLParser
import ckan.lib.helpers as ckan_helpers
import ckan.lib.search as search
import ckan.logic as logic
import ckan.model as model
import moment
from ckan.common import request, c, g, _
import ckan.lib.formatters as formatters
import subprocess
import json
import os
from urlparse import urljoin
from config_controller import GobArConfigController
from datetime import time
from dateutil import parser, tz
from pydatajson.core import DataJson
from pylons.config import config
from crontab import CronTab
import logging
import csv

logger = logging.getLogger(__name__)


def get_config_file_path():
    return "{}/production.ini".format(subprocess.check_output("echo $CKAN_DEFAULT", shell=True).strip())


def get_paster_path():
    return "{}/bin/paster".format(subprocess.check_output("echo $CKAN_HOME", shell=True).strip())


def _get_organizations_objs(organizations_branch, depth=0):
    organizations = []
    for tree_obj in organizations_branch:
        organization = ckan_helpers.get_organization(org=tree_obj['name'])
        organization['depth'] = depth
        if 'children' in tree_obj and len(tree_obj['children']) > 0:
            organization['children'] = _get_organizations_objs(tree_obj['children'], depth=depth + 1)
        organizations.append(organization)
    return organizations


def _count_total(organization):
    children_count = 0
    if 'children' in organization and len(organization['children']):
        for child_organization in organization['children']:
            children_count += _count_total(child_organization)
    return organization['package_count'] + children_count


def organizations_basic_info():

    def convert_organization_to_dict(organization, depth):
        current_organization = {}
        organization_id = organization.pop('id')
        current_organization['id'] = organization_id
        current_organization['name'] = organization.pop('name')
        current_organization['title'] = organization.pop('title')
        current_organization['depth'] = depth  # si depth == 0, la organización no es hija de otra
        current_organization['own_package_count'] = organizations_that_have_packages.pop(organization_id, 0)
        own_available_package_count = ckan_organizations_info.pop(current_organization['name'], {}).get('count', 0)
        children_data_dict = generate_children_data(organization.pop('children'), depth)
        current_organization['children'] = children_data_dict['dict_children']
        current_organization['total_package_count'] = children_data_dict['current_total_package_count'] \
                                                      + current_organization['own_package_count']
        current_organization['available_package_count'] = children_data_dict['current_available_package_count'] + \
                                                          own_available_package_count
        current_organization['active'] = current_organization['name'] == organization_in_request
        current_organization['display'] = not organization_in_request or current_organization['active']
        return current_organization

    def generate_children_data(group_tree_children, depth):
        dict_children = []
        current_available_package_count = 0
        current_total_package_count = 0
        for child in group_tree_children:
            converted_child = convert_organization_to_dict(child, depth+1)
            dict_children.append(converted_child)
            current_available_package_count += converted_child.get('available_package_count', 0)
            current_total_package_count += converted_child.get('total_package_count', 0)
        return {'dict_children': dict_children, 'current_available_package_count': current_available_package_count,
                'current_total_package_count': current_total_package_count}

    # Traemos las organizaciones
    organizations = get_organizations_tree()
    import pdb; pdb.set_trace()
    ckan_organizations_info = {item['name']: item for item in get_facet_items_dict('organization')}

    # Realizamos una query para conseguir las organizaciones que tienen datasets, y la cantidad de éstos
    query = search.PackageSearchQuery()
    q = {'q': '+capacity:public', 'fl': 'groups', 'facet.field': ['groups', 'owner_org'], 'facet.limit': -1, 'rows': 1}
    query.run(q)
    organizations_that_have_packages = query.facets.get('owner_org')

    # Transformamos cada organización en un dict para facilitar su uso, y agregamos información requerida
    organizations_data = []
    organization_in_request = ckan_helpers.get_request_param('organization')
    for organization in organizations:
        current_organization = convert_organization_to_dict(organization, 0)
        organizations_data.append(current_organization)

    return organizations_data


def get_organizations_tree():
    return logic.get_action('group_tree')({}, {'type': 'organization'})


def organization_tree():
    organizations_tree = logic.get_action('group_tree')({}, {'type': 'organization'})
    organizations = _get_organizations_objs(organizations_tree)
    for organization in organizations:
        organization['display_count'] = _count_total(organization)
    return organizations


def get_suborganizations_names(org_name=None):
    '''
    Consigue el 'name' de todas las suborganizaciones de una organización
    :param org_name: 'name' de la organización cuyas suborganizaciones necesitamos
    :return: una lista vacía o que contiene los 'name' de las suborganizaciones correspondientes
    '''
    if org_name is None:
        return []
    organizations = organization_tree()
    for organization in organizations:
        if organization.get('name') == org_name:
            if 'children' in organization:
                return list(map(lambda x: x['name'], organization['children']))
            break
    return []


def fetch_groups():
    data_dict_page_results = {
        'all_fields': True,
        'type': 'group',
        'limit': None,
        'offset': 0,
    }
    return logic.get_action('group_list')({}, data_dict_page_results)


def get_faceted_groups(items_limit=None):
    groups = fetch_groups()
    facets = get_facet_items_dict(facet='groups', limit=items_limit)
    facets_by_name = {}
    for facet in facets:
        facets_by_name[facet['name']] = facet
    for group in groups:
        group_name = group['name']
        if group_name in facets_by_name:
            group['facet_active'] = facets_by_name[group['name']]['active']
            group['facet_count'] = facets_by_name[group['name']]['count']
        else:
            group['facet_active'] = False
            group['facet_count'] = 0
    return groups


def get_facet_items_dict(facet, limit=None, exclude_active=False):
    # CKAN impone un límite de 10 para los temas. Puedo tener más de 10, por lo que no podría clickear el resto.
    c.search_facets_limits['groups'] = None
    return ckan_helpers.get_facet_items_dict(facet, limit, exclude_active)


def remove_url_param(key, value=None, replace=None, controller=None,
                     action=None, extras=None, alternative_url=None):
    if isinstance(key, basestring):
        keys = [key]
    else:
        keys = key

    params_nopage = [(k, v) for k, v in request.params.items() if k != 'page']
    params = list(params_nopage)
    if value:
        params.remove((keys[0], value))
    else:
        for key in keys:
            [params.remove((k, v)) for (k, v) in params[:] if k == key]
    if replace is not None:
        params.append((keys[0], replace))
    if alternative_url:
        return ckan_helpers._url_with_params(alternative_url, params)
    return ckan_helpers._create_url_with_params(params=params, controller=controller, action=action, extras=extras)


def get_groups_img_paths(groups):
    groups_with_path = {}
    for group in groups:
        groups_with_path[group['id']] = group['image_display_url']
    return groups_with_path


def join_groups(selected_groups):
    data_dict_page_results = {
        'all_fields': True,
        'type': 'group',
        'limit': None,
        'offset': 0,
    }
    groups = logic.get_action('group_list')({}, data_dict_page_results)
    for selected_group in selected_groups:
        for group in groups:
            if selected_group['name'] == group['name']:
                group['selected'] = True
    return sorted(groups, key=lambda k: k['display_name'].lower())


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
        if 'children' in organization and len(organization['children']) > 0:
            descendants += all_descendants(organization['children'])
    return descendants


def organization_filters():
    top_organizations = {}
    ancestors_relations = {}
    tree = organization_tree()
    for top_organization in tree:
        top_organization['count'] = 0
        top_organizations[top_organization['name']] = top_organization
        ancestors_relations[top_organization['name']] = top_organization['name']
        if 'children' in top_organization and len(top_organization['children']) > 0:
            children = all_descendants(top_organization['children'])
            for child_name in children:
                ancestors_relations[child_name] = top_organization['name']

    for organization in ckan_helpers.get_facet_items_dict('organization'):
        top_parent_name = ancestors_relations[organization['name']]
        if top_parent_name in top_organizations:
            top_organizations[top_parent_name]['count'] += organization['count']
    if ckan_helpers.get_request_param('organization') in top_organizations:
        top_organizations[ckan_helpers.get_request_param('organization')]['active'] = True

    top_organizations_with_results = [organization for organization in top_organizations.values() if
                                      organization['count'] > 0]
    sorted_organizations = sorted(top_organizations_with_results, key=lambda item: item['count'], reverse=True)

    org_limit = request.params.get('_organization_limit', g.facets_default_number)
    if org_limit != '':
        limit = int(org_limit)
    else:
        limit = None
    c.search_facets_limits['organization'] = limit
    if limit is not None and limit > 0:
        return sorted_organizations[:limit]
    return sorted_organizations


def get_theme_config(path=None, default=None):
    return GobArConfigController.get_theme_config(path, default)


def url_join(*args):
    return urljoin(*args)


def json_loads(json_string):
    return json.loads(json_string)


def license_options(existing_license_id=None):
    # En lugar de retornar una lista de tuplas, como hace el código original de CKAN, retorno una lista de licencias
    # para soportar el uso del campo 'license_ids'
    register = model.Package.get_license_register()
    sorted_licenses = sorted(register.values(), key=lambda x: x.title)
    return sorted_licenses


def id_belongs_to_license(id, license):
    return id == license.id or (hasattr(license, 'legacy_ids') and id in license.legacy_ids)


def get_license(id):
    for license in license_options():
        if id_belongs_to_license(id, license):
            return license
    return None


def get_license_title(license_id):
    for license in license_options():
        if id_belongs_to_license(license_id, license):
            return license.title
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
        filtered_freq = filter(lambda freq: freq[0] == freq_id, frequencies)
        if len(filtered_freq) > 0:
            return filtered_freq[0]
        return None
    return frequencies


def field_types(field_type_id=None):
    field_types = [
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
        filtered_field_type = filter(lambda field_type: field_type[0] == field_type_id, field_types)
        if len(filtered_field_type) > 0:
            return filtered_field_type[0]
        return None

    return field_types


def distribution_types(distribution_type_id=None):
    distribution_types = [
        ("file", u"Archivo de datos"),
        ("api", u"API"),
        ("code", u"Código"),
        ("documentation", u"Documentación")
    ]

    if distribution_type_id:
        filtered_distribution_type = \
            filter(lambda distribution_type: distribution_type[0] == distribution_type_id, distribution_types)
        if len(filtered_distribution_type) > 0:
            return filtered_distribution_type[0]
        return None

    return distribution_types


def special_field_types(special_field_type_id=None):
    special_field_types = [
        ("time_index", u"Índice de tiempo"),
    ]
    if special_field_type_id is not None:
        filtered_special_field_type = filter(lambda special_field_type: special_field_type[0] == special_field_type_id, special_field_types)
        if len(filtered_special_field_type) > 0:
            return filtered_special_field_type[0]
        return None
    return special_field_types


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
        if len(attributes.get(attr, '')) > 0:
            return True
    return False


def portal_andino_version():
    from ckanext.gobar_theme.actions import _get_portal_andino_version
    version = _get_portal_andino_version()
    version = version['portal-andino'] or 'Desarrollo'

    version = version.replace('release-', '')  # Elimino el release-
    version = version[:15]  # me quedo con los primeros 15 caracteres

    return version


def get_distribution_metadata(resource_id, package_id):
    # Se importa 'datajson_actions' en la función para evitar dependencias circulares con 'config_controller'
    import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
    json_dict = datajson_actions.get_data_json_contents()
    parser = HTMLParser()
    json_dict = parser.unescape(json_dict)
    json_dict = json.loads(json_dict)
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
    config = get_theme_config()
    data_dict_id = data_dict.get('id')
    if len(data_dict) > 1:
        data_dict.pop('id')

        config_item = config.get(object_dict_name, {})
        config_item.update({data_dict_id: data_dict})
        config[object_dict_name] = config_item

        GobArConfigController.set_theme_config(config)
        return config[object_dict_name][data_dict.get('id', data_dict_id)]
    return None


def get_resource_icon(resource, config):
    icon_url = resource.get('icon_url', None)
    if icon_url:
        return icon_url
    package_id = resource['package_id']
    id_to_search_with = '%s_%s_%s' % (
        get_package_organization(package_id).get('id', ''),
        resource['package_id'],
        resource['id']
    )
    if not config:
        config = get_theme_config()
    resource_in_config = config.get('resources', {}).get(id_to_search_with, None)
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
    except:
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
