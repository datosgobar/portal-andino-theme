#! coding: utf-8

import json
import os
import io
import re
import ckanext.gobar_theme.helpers as gobar_helpers
from ckan.config.environment import config
from pylons import response
import ckan.logic as logic
import ckan.plugins as p
import ckan.lib.base as base
import logging
logger = logging.getLogger(__name__)

CACHE_FILENAME = "/var/lib/ckan/theme_config/datajson_cache.json"
SUPERTHEME_TAXONOMY_URL = "http://datos.gob.ar/superThemeTaxonomy.json"
ANDINO_METADATA_VERSION = "1.1"


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


def update_datajson_cache():
    with open(CACHE_FILENAME, 'w+') as file:
        datajson = get_catalog_data()
        datajson['dataset'] = filter_dataset_fields(get_datasets_with_resources(get_ckan_datasets()) or [])
        # Guardo la renderización con Jinja del data.json en la cache
        renderization = base.render('datajson.html', extra_vars={'datajson': datajson})
        file.write(renderization)
        logger.info('Se actualizó la cache del data.json')
        return renderization


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
        if author_name is not None and author_name != '':
            publisher['name'] = author_name
        if author_email is not None and author_email != '':
            publisher['mbox'] = author_email
        source = get_field_from_list_and_delete(ds['extras'], 'source')
        contactPoint = {}
        maintainer = ds['maintainer']
        maintainer_email = ds['maintainer_email']
        if maintainer is not None and maintainer != '':
            contactPoint['fn'] = maintainer
        if maintainer_email is not None and maintainer_email != '':
            contactPoint['hasEmail'] = maintainer_email
        keyword = map(lambda kw: kw['display_name'], ds['tags'])
        superTheme = get_field_from_list_and_delete(ds['extras'], 'superTheme')
        if superTheme is None or superTheme == '':
            superTheme = get_field_from_list_and_delete(ds['extras'], 'globalGroups')
            if superTheme is not None and superTheme != '':
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
        accrualPeriodicity = get_field_from_list_and_delete(ds['extras'], 'accrualPeriodicity')
        if not accrualPeriodicity:
            get_field_from_list_and_delete(ds['extras'], 'updateFrequency')
        temporal = get_field_from_list_and_delete(ds['extras'], 'temporal')
        if temporal is None or temporal == '':
            temporal = get_field_from_list_and_delete(ds['extras'], 'dateRange')
        resources = clean_resources(ds['resources'])

        # Voy guardando los datos a mostrar en el data.json
        current_dataset.update({'title': ds['title']})
        current_dataset.update({'description': ds['notes']})
        current_dataset.update({'identifier': ds['id']})
        if issued is not None and issued != '':
            current_dataset.update({'issued': issued})
        if modified is not None and modified != '':
            current_dataset.update(({'modified': modified}))
        if ds['url'] is not None and ds['url'] != '':
            current_dataset.update({"landingPage": ds['url']})
        if ds['license_title'] is not None and ds['license_title']:
            current_dataset.update({"license": ds['license_title']})
        if country is not None and country != '':
            spatial = [country]
            if province is not None and province != '':
                spatial.append(province)
                if district is not None and district != '':
                    spatial.append(district)
            current_dataset.update({"spatial": spatial})
        elif ds.get('spatial', None) is not None:
            spatial = ds['spatial']
            if isinstance(spatial, basestring) and len(spatial):
                current_dataset.update({"spatial": spatial})
        if publisher != {}:
            current_dataset.update({"publisher": publisher})
        if contactPoint != {}:
            current_dataset.update({"contactPoint": contactPoint})
        if source is not None and source != '':
            current_dataset.update({"source": source})
        if resources is not None and resources != []:
            current_dataset.update({"distribution": resources})
        if keyword is not None and len(keyword):
            current_dataset.update({"keyword": keyword})
        if superTheme is not None:
            current_dataset.update({"superTheme": superTheme})
        if language is not None:
            current_dataset.update({"language": language})
        if theme is not None:
            current_dataset.update({"theme": theme})
        if accrualPeriodicity is not None:
            current_dataset.update(({"accrualPeriodicity": accrualPeriodicity}))
        if temporal is not None:
            current_dataset.update({"temporal": temporal})
        final_list.append(current_dataset)
    return final_list


def clean_resources(resources):
    final_resource_list = []
    for resource in resources:
        current_resource = {}
        current_resource['identifier'] = resource['id']
        if resource.get('format', None):
            current_resource['format'] = resource['format']
        current_resource['title'] = resource['name']
        current_resource['description'] = resource['description']
        if 'fileName' in resource and resource['fileName'] != '':
            current_resource['fileName'] = resource['fileName']
        if resource.get('resource_type', None):
            current_resource['type'] = resource['resource_type']
        if 'issued' in resource:
            current_resource['issued'] = resource['issued']
        elif 'created' in resource:
            current_resource['issued'] = resource['created']
        else:
            current_resource['issued'] = ''
        if 'modified' in resource:
            current_resource['modified'] = resource['modified']
        elif 'last_modified' in resource:
            current_resource['modified'] = resource['last_modified']
        else:
            current_resource['modified'] = ''
        if resource.get('license_id', None):
            current_resource['license'] = resource['license_id']
        if 'accessURL' in resource:
            current_resource['accessURL'] = resource['accessURL']
        else:
            current_resource['accessURL'] = \
                os.path.join(config.get('ckan.site_url'), 'dataset', resource['package_id'], 'resource', resource['id'])
        current_resource['downloadURL'] = generate_resource_downloadURL(resource)
        if resource.get('attributesDescription', []):
            current_resource['field'] = resource['attributesDescription']
            current_resource['attributes'] = tuple(resource['attributesDescription'])
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
                    fixed_attrDesc = json.loads(resource['attributesDescription'])
                    packages[i]['resources'][index]['attributesDescription'] = fixed_attrDesc
                except ValueError:
                    # logger.error('Fallo render de \'attributesDescription\'.') todo: logger?
                    pass
        except KeyError:
            pass
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
                # logger.info("landingPage generado para el dataset_id: %s.", packages[i]['name']) todo: logger?
        except TypeError:
            prepare_url = 'unknow'
            try:
                prepare_url = packages[i]['resources'][0]['url']
                prepare_url = prepare_url.split('resource')[0]
                # logger.info("landingPage generado para el dataset_id: %s, Tipo de datos: \" harvest\".",
                #             packages[i]['name'])                                              todo: logger?
            except IndexError:
                # logger.error("autogen \"landingpage\" fails.") todo: logger?
                pass
            packages[i].update({'url': prepare_url})
    return packages


def get_catalog_data():
    datajson = {}
    spatial = []
    spatial_config_fields = ['country', 'province', 'districts']
    for spatial_config_field in spatial_config_fields:
        spatial_config_field_value = gobar_helpers.get_theme_config(
            "portal-metadata.%s" % spatial_config_field, "")
        if spatial_config_field_value:
            spatial.extend(spatial_config_field_value.split(','))
    data_dict_page_results = {
        'all_fields': True,
        'type': 'group',
        'limit': None,
        'offset': 0,
    }
    groups = []
    for theme in logic.get_action('group_list')({}, data_dict_page_results):
        groups.append({'id': theme['name'],
                       'description': theme['description'],
                       'label': theme['display_name']
                       })
    datajson['version'] = ANDINO_METADATA_VERSION
    datajson['identifier'] = gobar_helpers.get_theme_config("portal-metadata.id", "") or ''
    datajson['title'] = gobar_helpers.get_theme_config("title.site-title", "") or ''
    datajson['description'] = gobar_helpers.get_theme_config("title.site-description", "") or ''
    datajson['superThemeTaxonomy'] = SUPERTHEME_TAXONOMY_URL
    datajson['publisher'] = {'mbox': gobar_helpers.get_theme_config("social.mail", ""),
                             'name': gobar_helpers.get_theme_config("title.site-organization", "") or ''}
    datajson['issued'] = \
        gobar_helpers.date_format_to_iso(
            gobar_helpers.get_theme_config("portal-metadata.launch_date", "")) or ''
    datajson['modified'] = \
        gobar_helpers.date_format_to_iso(
            gobar_helpers.get_theme_config("portal-metadata.last_updated", "")) or ''
    datajson['language'] = gobar_helpers.get_theme_config("portal-metadata.languages", "") or []
    datajson['license'] = gobar_helpers.get_theme_config("portal-metadata.license", "") or ''
    datajson['homepage'] = gobar_helpers.get_theme_config('portal-metadata.homepage') or ''
    datajson['rights'] = gobar_helpers.get_theme_config("portal-metadata.licence_conditions", "") or ''
    datajson['spatial'] = spatial or []
    datajson['themeTaxonomy'] = groups
    return datajson


