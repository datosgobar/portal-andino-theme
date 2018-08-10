#! coding: utf-8

import json
import os
import io
import re
import ckanext.gobar_theme.helpers as gobar_helpers
import ckan.lib.jobs as jobs
from ckan.config.environment import config
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
    context = {'model': model, 'session': model.Session, 'user': c.user}
    delete.job_clear(context, {'queues': [ANDINO_DATAJSON_QUEUE]})
    jobs.enqueue(update_datajson_cache, queue=ANDINO_DATAJSON_QUEUE)
    jobs.enqueue(update_catalog, queue=ANDINO_DATAJSON_QUEUE)


def update_datajson_cache():
    file_descriptor, file_path = tempfile.mkstemp(suffix='.json', dir=CACHE_DIRECTORY)
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

    os.rename(file_path, CACHE_FILENAME)
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
        issued = get_field_from_list_and_delete(ds['extras'], 'issued') or ds['metadata_created']
        modified = get_field_from_list_and_delete(ds['extras'], 'modified') or ds['metadata_modified']
        country = get_field_from_list_and_delete(ds['extras'], 'country')
        province = get_field_from_list_and_delete(ds['extras'], 'province')
        district = get_field_from_list_and_delete(ds['extras'], 'district')
        publisher = {}
        author_name = ds['author']
        author_email = ds['author_email']
        if author_name:
            publisher['name'] = author_name
        if author_email:
            publisher['mbox'] = author_email
        source = get_field_from_list_and_delete(ds['extras'], 'source')
        maintainer = ds['maintainer']
        maintainer_email = ds['maintainer_email']
        contactPoint = {}
        if maintainer:
            contactPoint['fn'] = maintainer
        if maintainer_email:
            contactPoint['hasEmail'] = maintainer_email
        keyword = map(lambda kw: kw['display_name'], ds['tags'])
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
        theme = map(lambda th: th['name'], ds['groups'])
        accrualPeriodicity = get_field_from_list_and_delete(ds['extras'], 'accrualPeriodicity') or \
                             get_field_from_list_and_delete(ds['extras'], 'updateFrequency')
        temporal = get_field_from_list_and_delete(ds['extras'], 'temporal') or \
                   get_field_from_list_and_delete(ds['extras'], 'dateRange')
        resources = clean_resources(ds['resources'])

        # Voy guardando los datos a mostrar en el data.json
        current_dataset.update({'title': ds['title']})                                                           # title
        current_dataset.update({'description': ds['notes']})                                               # description
        current_dataset.update({'identifier': ds['id']})                                                            # id
        if issued:
            current_dataset.update({'issued': issued})                                                          # issued
        if modified:
            current_dataset.update(({'modified': modified}))                                                  # modified
        if ds['url']:
            current_dataset.update({"landingPage": ds['url']})                                                     # url
        if ds['license_title']:
            current_dataset.update({"license": ds['license_title']})                                           # license
        if country and country != "None":
            spatial = [country]
            if province:
                spatial.append(province)
                if district:
                    spatial.append(district)
            current_dataset.update({"spatial": spatial})                                                       # spatial
        elif ds.get('spatial', None):
            spatial = ds['spatial']
            if isinstance(spatial, basestring) and len(spatial):
                current_dataset.update({"spatial": spatial})
        if publisher:
            current_dataset.update({"publisher": publisher})                                                 # publisher
        if contactPoint:
            current_dataset.update({"contactPoint": contactPoint})                                        # contactPoint
        if source:
            current_dataset.update({"source": source})                                                          # source
        if resources:
            current_dataset.update({"distribution": resources})                                              # resources
        if keyword:
            current_dataset.update({"keyword": keyword})                                                       # keyword
        if superTheme:
            current_dataset.update({"superTheme": superTheme})                                              # superTheme
        if language:
            current_dataset.update({"language": language})                                                    # language
        if theme:
            current_dataset.update({"theme": theme})                                                             # theme
        if accrualPeriodicity:
            current_dataset.update(({"accrualPeriodicity": accrualPeriodicity}))                    # accrualPeriodicity
        if temporal:
            current_dataset.update({"temporal": temporal})                                                    # temporal
        final_list.append(current_dataset)
    return final_list


def clean_resources(resources):
    final_resource_list = []
    for resource in resources:
        current_resource = {}

        # Recolecto datos del recurso
        format = resource.get('format', None)
        fileName = resource.get('fileName', None)
        url = resource.get('url', None)
        url_type = resource.get('url_type', None)
        type = resource.get('resource_type', None)
        issued = resource.get('issued', None) or resource.get('created', None)
        modified = resource.get('modified', None) or resource.get('last_modified', None)
        license = resource.get('license_id', None)
        accessURL = resource.get('accessURL', None) or \
                    gobar_helpers.get_current_url_for_resource(resource['package_id'], resource['id'])
        field = resource.get('attributesDescription', [])
        for element in field:
            for key in element.keys():
                if not element[key]:
                    element.pop(key)

        # Guardo todos los elementos que no estén vacíos ni sean None
        current_resource['identifier'] = resource['id']                                                     # identifier
        if format:
            current_resource['format'] = resource['format']                                                     # format
        current_resource['title'] = resource['name']                                                             # title
        current_resource['description'] = resource['description']                                          # description
        if fileName:
            current_resource['fileName'] = resource['fileName']                                               # fileName
        if url_type:
            if url_type == 'upload' and url and type != 'api' and '/' in url:
                # Como se subió un archivo, queremos asegurarnos de que el fileName
                # sea correcto; lo buscamos en la URL
                last_slash_position = url.rfind('/')
                current_resource['fileName'] = url[last_slash_position+1:]                           # fileName (upload)
            if type:
                current_resource['type'] = type                                                                   # type
        if issued:
            current_resource['issued'] = issued                                                                 # issued
        if modified:
            current_resource['modified'] = modified                                                           # modified
        if license:
            current_resource['license'] = license                                                              # license
        if accessURL:
            current_resource['accessURL'] = accessURL                                                        # accessURL
        current_resource['downloadURL'] = generate_resource_downloadURL(resource)                          # downloadURL
        if field:
            current_resource['field'] = field                                                                    # field
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

        query = p.toolkit.get_action('package_search')({}, search_data_dict)
        if len(query['results']):
            dataset_list.extend(query['results'])
            page += 1
        else:
            break
    return dataset_list


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
            logger.error(u"Fallo durante la transformación de 'attributesDescription' del package %s.", packages[i].get('id'))
        ckan_host = ''
        try:
            ckan_host = re.match(
                r'(?:http)s?:\/\/([\w][^\/=\s]+)\/?|(^w{3}[\.\w][^\/\=\s]{2,})\/?',
                packages[i]['resources'][0]['url']).group(0)
        except Exception:
            pass
        try:
            if len(packages[i]['url']) < 1:
                packages[i]['url'] = '{host}/dataset/{dataset_id}'.format(
                    host=ckan_host[:-1],
                    dataset_id=packages[i]['name'])
                logger.info("landingPage generado para el dataset_id: %s.", packages[i]['name'])
        except TypeError:
            prepare_url = 'unknow'
            try:
                prepare_url = packages[i]['resources'][0]['url']
                prepare_url = prepare_url.split('resource')[0]
                logger.info("landingPage generado para el dataset_id: %s, Tipo de datos: \" harvest\".",
                            packages[i]['name'])
            except IndexError:
                logger.error("autogen \"landingpage\" fails.")
            packages[i].update({'url': prepare_url})
    return packages


def get_catalog_data():
    datajson = {}
    identifier = gobar_helpers.get_theme_config("portal-metadata.id", "")
    title = gobar_helpers.get_theme_config("title.site-title", "")
    description = gobar_helpers.get_theme_config("title.site-description", "")
    publisher = {}
    publisher_mbox = gobar_helpers.get_theme_config("social.mail", "")
    publisher_name = gobar_helpers.get_theme_config("title.site-organization", "")
    if publisher_mbox:
        publisher['mbox'] = publisher_mbox
    if publisher_name:
        publisher['name'] = publisher_name
    issued = gobar_helpers.date_format_to_iso(gobar_helpers.get_theme_config("portal-metadata.launch_date", ""))
    modified = gobar_helpers.date_format_to_iso(gobar_helpers.get_theme_config("portal-metadata.last_updated", ""))
    language = gobar_helpers.get_theme_config("portal-metadata.languages", "")
    license = gobar_helpers.get_theme_config("portal-metadata.license", u"CC-BY-4.0")
    homepage = gobar_helpers.get_theme_config('portal-metadata.homepage')
    rights = gobar_helpers.get_theme_config("portal-metadata.licence_conditions", "")
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

    datajson['version'] = ANDINO_METADATA_VERSION
    datajson['superThemeTaxonomy'] = SUPERTHEME_TAXONOMY_URL
    if identifier:
        datajson['identifier'] = identifier
    if title:
        datajson['title'] = title
    if description:
        datajson['description'] = description
    if publisher:
        datajson['publisher'] = publisher
    if issued:
        datajson['issued'] = issued
    if modified:
        datajson['modified'] = modified
    if language:
        datajson['language'] = language
    if license:
        datajson['license'] = license
    if homepage:
        datajson['homepage'] = homepage
    if rights:
        datajson['rights'] = rights
    if spatial:
        datajson['spatial'] = spatial
    if groups:
        datajson['themeTaxonomy'] = groups
    return datajson


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
    new_catalog_filename = '%s/catalog.xlsx' % tempfile.mkdtemp(dir=CACHE_DIRECTORY)
    writers.write_xlsx_catalog(catalog, new_catalog_filename)
    os.rename(new_catalog_filename, XLSX_FILENAME)
    os.rmdir(new_catalog_filename.replace('/catalog.xlsx', ''))


def read_from_catalog(stream):
    with open(XLSX_FILENAME, 'rb') as file_handle:
        stream.write(file_handle.read())
    return stream.getvalue()
