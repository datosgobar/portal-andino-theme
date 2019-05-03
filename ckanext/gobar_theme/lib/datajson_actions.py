#! coding: utf-8
# pylint: disable-all

import json
import os
import io
import re
import ckanext.gobar_theme.helpers as gobar_helpers
import ckan.lib.jobs as jobs
import ckan.logic.action.delete as delete
from ckan.common import c
import ckan.model as model
import ckan.logic as logic
import ckan.plugins as p
import logging
import tempfile

logger = logging.getLogger(__name__)

CACHE_DIRECTORY = "/var/lib/ckan/theme_config/"
CACHE_FILENAME = CACHE_DIRECTORY + "datajson_cache.json"
XLSX_FILENAME = CACHE_DIRECTORY + "catalog.xlsx"
SUPERTHEME_TAXONOMY_URL = "http://datos.gob.ar/superThemeTaxonomy.json"
ANDINO_METADATA_VERSION = "1.1"
ANDINO_DATAJSON_QUEUE = 'andino-datajson-queue'


# ============================ datajson section ============================ #


def get_data_json_contents():
    try:
        with open(CACHE_FILENAME, 'r+') as file:
            content = file.read()
            if content:
                logger.info('Accediendo a la caché del data.json.')
                return content
            else:
                logger.info('La caché del data.json se encuentra vacía - la regeneramos.')
                return update_datajson_cache()
    except IOError:
        logger.info('IOError, asumimos que hay que regenerar el data.json cacheado.')
        return update_datajson_cache()


def enqueue_update_datajson_cache_tasks():
    # Las funciones que usamos de RQ requieren que se les envíe el context para evitar problemas de autorización
    try:
        context = {'model': model, 'session': model.Session, 'user': c.user}
        delete.job_clear(context, {'queues': [ANDINO_DATAJSON_QUEUE]})
    except logic.NotAuthorized:
        logger.info(u'Usuario %s no tiene permisos para administrar colas de trabajo. '
                    u'No es posible limpiar las colas previo actualización de data.json', c.user)
    jobs.enqueue(update_datajson_cache, queue=ANDINO_DATAJSON_QUEUE)
    jobs.enqueue(update_catalog, queue=ANDINO_DATAJSON_QUEUE)


def update_datajson_cache():
    file_descriptor, file_path = tempfile.mkstemp(suffix='.json', dir=CACHE_DIRECTORY)
    renderization = generate_new_cache_file(file_descriptor)
    os.rename(file_path, CACHE_FILENAME)
    return renderization


def generate_new_cache_file(file_descriptor):
    with os.fdopen(file_descriptor, 'w+') as datajson_cache:
        datajson = generate_datajson_info()

        # Creamos un TemplateLoader
        import jinja2
        loader = jinja2.PackageLoader('ckanext.gobar_theme', 'templates')
        environment = jinja2.Environment(loader=loader)
        template = environment.get_template('datajson.html')

        # Guardo la renderización con Jinja del data.json en la caché auxiliar
        renderization = template.render({
            'datajson': datajson,
            'h': {
                'jsondump': gobar_helpers.jsondump,
            },
        })

        datajson_cache.write(renderization)
        logger.info('Se actualizó la cache del data.json')
        return renderization


def generate_datajson_info():
    datajson = get_catalog_data()
    datajson['dataset'] = filter_dataset_fields(get_datasets_with_resources(get_ckan_datasets()) or [])
    return datajson


def get_field_from_list_and_delete(list, wanted_field):
    for field in list:
        if field['key'] == wanted_field:
            result = field['value']
            list.remove(field)
            return result
    return None


def filter_dataset_fields(dataset_list):
    final_list = []
    for ds in dataset_list:
        current_dataset = {}

        # Consigo los elementos existentes en listas que voy a necesitar
        country = get_field_from_list_and_delete(ds['extras'], 'country')
        province = get_field_from_list_and_delete(ds['extras'], 'province')
        district = get_field_from_list_and_delete(ds['extras'], 'district')
        publisher = {}
        set_nonempty_value(publisher, 'name', ds['author'])
        set_nonempty_value(publisher, 'mbox', ds['author_email'])
        contactPoint = {}
        set_nonempty_value(contactPoint, 'fn', ds['maintainer'])
        set_nonempty_value(contactPoint, 'hasEmail', ds['maintainer_email'])
        superTheme = get_field_from_list_and_delete(ds['extras'], 'superTheme')
        if not superTheme:
            superTheme = get_field_from_list_and_delete(ds['extras'], 'globalGroups')
            if superTheme:
                superTheme = eval(superTheme)
            else:
                superTheme = []
        else:
            superTheme = eval(superTheme)
        language = get_field_from_list_and_delete(ds['extras'], 'language')
        if isinstance(language, (unicode, str)):
            language_list = []
            try:
                language_list = json.loads(language)
            except ValueError:
                if "{" or "}" in language:
                    lang = language.replace('{', '').replace('}', '').split(',')
                else:
                    lang = language
                if ',' in lang:
                    lang = lang.split(',')
                else:
                    lang = [lang]
                    language_list = json.loads(lang)
            language = language_list

        # Voy guardando los datos a mostrar en el data.json
        set_nonempty_value(current_dataset, 'title', ds['title'])
        set_nonempty_value(current_dataset, 'description', ds['notes'])
        set_nonempty_value(current_dataset, 'identifier', ds['id'])
        set_nonempty_value(current_dataset, 'issued',
                           get_field_from_list_and_delete(ds['extras'], 'issued') or ds['metadata_created'])
        set_nonempty_value(current_dataset, 'modified',
                           get_field_from_list_and_delete(ds['extras'], 'modified') or ds['metadata_modified'])
        set_nonempty_value(current_dataset, 'landingPage', ds['url'])
        set_nonempty_value(current_dataset, 'license', ds['license_title'])
        if country and country != "None":
            spatial = [country]
            if province:
                spatial.append(province)
                if district:
                    spatial.append(district)
            current_dataset.update({"spatial": spatial})
        elif ds.get('spatial', None):
            spatial = ds['spatial']
            if isinstance(spatial, basestring) and len(spatial):
                current_dataset.update({"spatial": spatial})
        set_nonempty_value(current_dataset, 'publisher', publisher)
        set_nonempty_value(current_dataset, 'contactPoint', contactPoint)
        set_nonempty_value(current_dataset, 'source', get_field_from_list_and_delete(ds['extras'], 'source'))
        set_nonempty_value(current_dataset, 'distribution', clean_resources(ds['resources']))
        set_nonempty_value(current_dataset, 'keyword', map(lambda kw: kw['display_name'], ds['tags']))
        set_nonempty_value(current_dataset, 'superTheme', superTheme)
        set_nonempty_value(current_dataset, 'language', language)
        set_nonempty_value(current_dataset, 'theme', map(lambda th: th['name'], ds['groups']))
        set_nonempty_value(current_dataset, 'accrualPeriodicity',
                           get_field_from_list_and_delete(ds['extras'], 'accrualPeriodicity')
                           or get_field_from_list_and_delete(ds['extras'], 'updateFrequency'))
        set_nonempty_value(current_dataset, 'temporal', get_field_from_list_and_delete(ds['extras'], 'temporal') or
                           get_field_from_list_and_delete(ds['extras'], 'dateRange'))
        final_list.append(current_dataset)
    return final_list


def clean_resources(resources):
    final_resource_list = []
    for resource in resources:
        current_resource = {}

        # Recolecto cierta información del recurso
        resource_format = resource.get('format')
        if resource_format:
            resource_format.upper()
        url = resource.get('url')
        url_type = resource.get('url_type')
        resource_type = resource.get('resource_type')
        field = resource.get('attributesDescription', [])
        filename = resource.get('fileName')
        for element in field:
            for key in element.keys():
                if not element[key]:
                    element.pop(key)

        # Guardo todos los datos que no estén vacíos ni sean None
        set_nonempty_value(current_resource, 'identifier', resource.get('id'))
        set_nonempty_value(current_resource, 'format', resource_format)
        set_nonempty_value(current_resource, 'title', resource.get('name'))
        set_nonempty_value(current_resource, 'description', resource.get('description'))
        set_nonempty_value(current_resource, 'fileName', filename)
        set_nonempty_value(current_resource, 'type', resource_type)
        if url_type == 'upload' and url and resource_type != 'api' and '/' in url:
            # Como se subió un archivo, queremos asegurarnos de que el fileName sea correcto; lo buscamos en la URL
            current_resource['fileName'] = filename or url.rsplit('/', 1)[-1]
        set_nonempty_value(current_resource, 'issued', resource.get('issued') or resource.get('created'))
        set_nonempty_value(current_resource, 'modified',
                           resource.get('modified') or resource.get('last_modified'))
        set_nonempty_value(current_resource, 'license', resource.get('license_id'))
        set_nonempty_value(current_resource, 'accessURL', resource.get('accessURL') or
                           gobar_helpers.get_current_url_for_resource(resource['package_id'], resource['id']))
        set_nonempty_value(current_resource, 'downloadURL', generate_resource_downloadURL(resource))
        set_nonempty_value(current_resource, 'field', field)
        final_resource_list.append(current_resource)
    return final_resource_list


def generate_resource_downloadURL(resource):
    downloadURL = resource.get('url').strip()
    if '' == downloadURL:
        return None
    return downloadURL


def get_ckan_datasets(org=None, with_private=True):
    n = 500
    page = 1
    dataset_list = []

    q = '+capacity:public' if not with_private else '*:*'

    fq = 'dataset_type:dataset'
    if org:
        fq += " AND organization:" + org

    while True:
        search_data_dict = {
            'q': q,
            'fq': fq,
            'sort': 'metadata_modified desc',
            'rows': n,
            'start': n * (page - 1),
        }

        context = prepare_context_variable()
        query = logic.action.get.package_search(context, search_data_dict)
        if query['results']:
            dataset_list.extend(query['results'])
            page += 1
        else:
            break
    return dataset_list


def prepare_context_variable():
    return {'model': model, 'session': model.Session,
            'user': c.user or c.author, 'for_view': True,
            'auth_user_obj': c.userobj}


def get_datasets_with_resources(packages):
    for i in range(0, len(packages)):
        try:
            for index, resource in enumerate(packages[i]['resources']):
                try:
                    attributes_description_as_dict = json.loads(resource.get('attributesDescription', '[]'))
                    packages[i]['resources'][index]['attributesDescription'] = attributes_description_as_dict
                except ValueError:
                    attributes_description_as_dict = []
                    logger.error('Fallo render de \'attributesDescription\'.')
                except KeyError as e:
                    logger.error(u'Error transformando attributesDescription de %s', resource)
                    raise e
        except KeyError:
            logger.error(u"Fallo durante la transformación de 'attributesDescription' del package %s.",
                         packages[i].get('id'))
        ckan_host = ''
        try:
            ckan_host = re.match(
                r'(?:http)s?:\/\/([\w][^\/=\s]+)\/?|(^w{3}[\.\w][^\/\=\s]{2,})\/?',
                packages[i]['resources'][0]['url']).group(0)
        except Exception:
            pass
        try:
            if not packages[i]['url']:
                packages[i]['url'] = '{host}/dataset/{dataset_id}'.format(
                    host=ckan_host[:-1],
                    dataset_id=packages[i]['name'])
        except TypeError:
            prepare_url = 'unknow'
            try:
                prepare_url = packages[i]['resources'][0]['url']
                prepare_url = prepare_url.split('resource')[0]
            except IndexError:
                logger.error("autogen \"landingpage\" fails.")
            packages[i].update({'url': prepare_url})
    return packages


def get_catalog_data():
    datajson = {}
    publisher = {}
    set_nonempty_value(publisher, 'mbox', gobar_helpers.get_theme_config("social.mail", ""))
    set_nonempty_value(publisher, 'name', gobar_helpers.get_theme_config("title.site-organization", ""))
    spatial = []
    spatial_config_fields = ['country', 'province', 'districts']
    for spatial_config_field in spatial_config_fields:
        spatial_config_field_value = gobar_helpers.get_theme_config(
            "portal-metadata.%s" % spatial_config_field, "")
        if spatial_config_field_value and spatial_config_field_value != "None":
            spatial.extend(spatial_config_field_value.split(','))
    data_dict_page_results = {
        'all_fields': True,
        'type': 'group',
        'limit': None,
        'offset': 0,
    }
    groups = []
    for theme in logic.get_action('group_list')({}, data_dict_page_results):
        theme_attributes = {}
        theme_name = theme['name']
        if theme_name:
            theme_attributes['id'] = theme_name
        theme_description = theme['display_name']
        if theme_description:
            theme_attributes['description'] = theme_description
        theme_label = theme['display_name']
        if theme_label:
            theme_attributes['label'] = theme['display_name']
        if theme_attributes:
            groups.append(theme_attributes)

    set_nonempty_value(datajson, 'version', ANDINO_METADATA_VERSION)
    set_nonempty_value(datajson, 'superThemeTaxonomy', SUPERTHEME_TAXONOMY_URL)
    set_nonempty_value(datajson, 'identifier', gobar_helpers.get_theme_config("portal-metadata.id", ""))
    set_nonempty_value(datajson, 'title', gobar_helpers.get_theme_config("title.site-title", ""))
    set_nonempty_value(datajson, 'description', gobar_helpers.get_theme_config("title.site-description", ""))
    set_nonempty_value(datajson, 'publisher', publisher)
    set_nonempty_value(datajson, 'issued', gobar_helpers.date_format_to_iso(
        gobar_helpers.get_theme_config("portal-metadata.launch_date", "")))
    set_nonempty_value(datajson, 'modified', gobar_helpers.date_format_to_iso(
        gobar_helpers.get_theme_config("portal-metadata.last_updated", "")))
    set_nonempty_value(datajson, 'language', gobar_helpers.get_theme_config("portal-metadata.languages", ""))
    set_nonempty_value(datajson, 'license', gobar_helpers.get_theme_config("portal-metadata.license", u"CC-BY-4.0"))
    set_nonempty_value(datajson, 'homepage', gobar_helpers.get_theme_config('portal-metadata.homepage'))
    set_nonempty_value(datajson, 'rights', gobar_helpers.get_theme_config("portal-metadata.licence_conditions", ""))
    set_nonempty_value(datajson, 'spatial', spatial)
    set_nonempty_value(datajson, 'themeTaxonomy', groups)
    return datajson


def set_nonempty_value(dict, key, value):
    if value:
        dict[key] = value


# ============================ Catalog section ============================ #


def get_catalog_xlsx():
    with io.BytesIO() as stream:
        try:
            # Trato de leer el catalog.xlsx si ya fue generado
            return read_from_catalog(stream)
        except IOError:
            update_catalog()
            return read_from_catalog(stream)


def update_catalog():
    from pydatajson import writers, DataJson
    # Chequeo que la caché del datajson exista antes de pasar su path como parámetro
    if not os.path.isfile(CACHE_FILENAME):
        # No existe, así que la genero
        update_datajson_cache()
    catalog = DataJson(CACHE_FILENAME)
    catalog['themeTaxonomy'] = catalog.get('themeTaxonomy', [])
    new_catalog_filename = '%s/catalog.xlsx' % tempfile.mkdtemp(dir=CACHE_DIRECTORY)
    writers.write_xlsx_catalog(catalog, new_catalog_filename)
    os.rename(new_catalog_filename, XLSX_FILENAME)
    os.rmdir(new_catalog_filename.replace('/catalog.xlsx', ''))


def read_from_catalog(stream):
    with open(XLSX_FILENAME, 'rb') as file_handle:
        stream.write(file_handle.read())
    return stream.getvalue()
