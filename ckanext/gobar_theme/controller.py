#coding: utf-8
from ckan.controllers.home import HomeController
from ckan.controllers.api import ApiController
from ckan.config.environment import config
from ckan.common import c
import ckan.logic as logic
import ckan.model as model
import ckan.lib.base as base
from ckan.lib.base import request
import json
import ckan.plugins as p
from ckanext.googleanalytics.controller import GAApiController
import ckanext.gobar_theme.helpers as gobar_helpers
import re
import os


class GobArHomeController(HomeController):
    def _list_groups(self):
        context = {
            'model': model,
            'session': model.Session,
            'user': c.user or c.author
        }
        data_dict_page_results = {
            'all_fields': True,
            'type': 'group',
            'limit': None,
            'offset': 0,
        }
        return logic.get_action('group_list')(context, data_dict_page_results)

    def _featured_packages(self):
        context = {
            'model': model,
            'session': model.Session,
            'user': c.user or c.author,
            'for_view': True
        }
        data_dict = {
            'q': ''
        }
        search = logic.get_action('package_search')(context, data_dict)
        if 'results' in search:
            results = search['results']
            featured_packages = []
            for result in results:
                for extra_pair in result['extras']:
                    if extra_pair['key'] == 'home_featured' and extra_pair['value'] == 'true':
                        featured_packages.append(result)

            segmented_packages = [featured_packages[n:n + 2] for n in range(len(featured_packages))[::2]]
            return segmented_packages
        return []

    def _packages_with_resource_type_equal_to_api(self):
        context = {
            'model': model,
            'session': model.Session,
            'user': c.user or c.author
        }
        data_dict = {
            'query': 'resource_type:api',
            'limit': None,
            'offset': 0,
        }
        return logic.get_action('resource_search')(context, data_dict).get('results', [])

    def index(self):
        c.groups = self._list_groups()
        c.sorted_groups = sorted(c.groups, key=lambda x: x['display_name'].lower())
        c.featured_packages = self._featured_packages()
        return super(GobArHomeController, self).index()

    def about(self):
        return base.render('about.html')

    def about_ckan(self):
        return base.render('about_ckan.html')

    def apis(self):
        c.apis = self._packages_with_resource_type_equal_to_api()
        return base.render('apis/apis.html')

    def view_about_section(self, title):
        sections = gobar_helpers.get_theme_config('about.sections', [])

        for section in sections:
            if section['title'] == title:
                # la variable `section` contiene la sección buscada
                break
        else:
            base.abort(404, u'Sección no encontrada')

        return base.render('section_view.html', extra_vars={'section': section})

    def datajson(self):
        datajson = {}
        spatial = []
        spatial_config_fields = ['country', 'province', 'districts']
        for spatial_config_field in spatial_config_fields:
            spatial_config_field_value = gobar_helpers.get_theme_config("portal-metadata.%s" % spatial_config_field, "")
            if spatial_config_field_value:
                spatial.extend(spatial_config_field_value.split(','))
        data_dict_page_results = {
            'all_fields': True,
            'type': 'group',
            'limit': None,
            'offset': 0,
        }
        groups = []

        datajson['version'] = gobar_helpers.portal_andino_version() or ''
        datajson['identifier'] = gobar_helpers.get_theme_config("portal-metadata.id", "") or ''
        datajson['title'] = gobar_helpers.get_theme_config("title.site-title", "") or ''
        datajson['description'] = gobar_helpers.get_theme_config("title.site-description", "") or ''
        datajson['superThemeTaxonomy'] = "http://datos.gob.ar/superThemeTaxonomy.json"
        datajson['publisher'] = {'mbox': gobar_helpers.get_theme_config("social.mail", ""),
                                 'name': gobar_helpers.get_theme_config("title.site-organization", "") or ''}
        datajson['issued'] = \
            gobar_helpers.date_format_to_iso(gobar_helpers.get_theme_config("portal-metadata.launch_date", "")) or ''
        datajson['modified'] = \
            gobar_helpers.date_format_to_iso(gobar_helpers.get_theme_config("portal-metadata.last_updated", "")) or ''
        datajson['language'] = gobar_helpers.get_theme_config("portal-metadata.languages", "") or []
        datajson['license'] = gobar_helpers.get_theme_config("portal-metadata.license", "") or ''
        datajson['homepage'] = gobar_helpers.get_theme_config('portal-metadata.homepage') or ''
        datajson['rights'] = gobar_helpers.get_theme_config("portal-metadata.licence_conditions", "") or ''
        datajson['spatial'] = spatial or []
        for theme in logic.get_action('group_list')({}, data_dict_page_results):
            groups.append({'id': theme['name'],
                           'description': theme['description'],
                           'label': theme['display_name']
                           })
        datajson['themeTaxonomy'] = groups
        datajson['dataset'] = \
            self.filter_dataset_fields(self.get_datasets_with_resources(self.get_ckan_datasets()) or [])

        return base.render('datajson.html', extra_vars={'datajson': datajson})

    def get_field_from_list_and_delete(self, list, wanted_field):
        for field in list:
            if field['key'] == wanted_field:
                result = field['value']
                list.remove(field)
                return result
        return None

    def filter_dataset_fields(self, dataset_list):
        final_list = []
        for dataset in dataset_list:
            current_dataset = {}

            # Consigo los elementos existentes en listas que voy a necesitar
            issued = self.get_field_from_list_and_delete(dataset['extras'], 'issued') or \
                     self.get_field_from_list_and_delete(dataset['extras'], 'metadata_created')
            modified = self.get_field_from_list_and_delete(dataset['extras'], 'modified') or \
                       self.get_field_from_list_and_delete(dataset['extras'], 'metadata_modified')
            country = self.get_field_from_list_and_delete(dataset['extras'], 'country')
            province = self.get_field_from_list_and_delete(dataset['extras'], 'province')
            district = self.get_field_from_list_and_delete(dataset['extras'], 'district')
            publisher = {'name': dataset['author']['name'],
                         'mbox': dataset['author_email']}
            source = self.get_field_from_list_and_delete(dataset['extras'], 'source')
            contactPoint = {'fn': dataset['maintainer'], 'hasEmail': dataset['maintainer_email']}
            keyword = map(lambda kw: kw['display_name'], dataset['tags'])
            superTheme = eval(self.get_field_from_list_and_delete(dataset['extras'], 'superTheme'))
            if superTheme is None or superTheme == []:
                superTheme = eval(self.get_field_from_list_and_delete(dataset['extras'], 'globalGroups'))
            language = self.get_field_from_list_and_delete(dataset['extras'], 'language')
            theme = map(lambda th: th['name'], dataset['groups'])
            accrualPeriodicity = self.get_field_from_list_and_delete(dataset['extras'], 'accrualPeriodicity')
            if accrualPeriodicity is None:
                self.get_field_from_list_and_delete(dataset['extras'], 'updateFrequency')
            temporal = self.get_field_from_list_and_delete(dataset['extras'], 'temporal')
            if temporal is None or temporal == '':
                temporal = self.get_field_from_list_and_delete(dataset['extras'], 'dateRange')
            spatial = ["None"]

            # Voy guardando los datos a mostrar en el data.json
            current_dataset.update({'title': dataset['title']})
            current_dataset.update({'description': dataset['notes']})
            current_dataset.update({'identifier': dataset['id']})
            if issued:
                current_dataset.update({'issued': issued})
            if modified:
                current_dataset.update(({'modified': modified}))
            if dataset['url']:
                current_dataset.update({"landingPage": dataset['url']})
            if dataset['license_title']:
                current_dataset.update({"license": dataset['license_title']})
            spatial[0] = country
            if province != '' and district != '':
                spatial.append(province)
                spatial.append(district)
            elif province != '':
                spatial.append(province)
            if country != 'None':
                current_dataset.update({"spatial": spatial})
            current_dataset.update({"publisher": publisher})
            if contactPoint['fn'] != '' or contactPoint['hasEmail'] != '':
                current_dataset.update({"contactPoint": contactPoint})
            if source:
                current_dataset.update({"source": source})
            current_dataset.update({"distribution": self.clean_resources(dataset['resources'])})
            if len(keyword):
                current_dataset.update({"keyword": keyword})
            current_dataset.update({"superTheme": superTheme})
            if len(language):
                current_dataset.update({"language": language})
            if theme is not None:
                current_dataset.update({"theme": theme})
            if accrualPeriodicity is not None:
                current_dataset.update(({"accrualPeriodicity": accrualPeriodicity}))
            if temporal:
                current_dataset.update({"temporal": temporal})
            final_list.append(current_dataset)
        return final_list

    def clean_resources(self, resources):
        final_resource_list = []
        for resource in resources:
            current_resource = {}
            current_resource['identifier'] = resource['id']
            if resource['format'] != '':
                current_resource['format'] = resource['format']
            current_resource['title'] = resource['name']
            current_resource['description'] = resource['description']
            if 'fileName' in resource and resource['fileName'] != '':
                current_resource['fileName'] = resource['fileName']
            if resource['resource_type'] is not None:
                current_resource['type'] = resource['resource_type']
            if resource['issued'] != '':
                current_resource['issued'] = resource['issued']
            if resource['modified'] != '':
                current_resource['modified'] = resource['modified']
            if resource['license_id'] != '':
                current_resource['license'] = resource['license_id']
            current_resource['accessURL'] = \
                os.path.join(config.get('ckan.site_url'), 'dataset', resource['package_id'], 'resource', resource['id'])
            current_resource['downloadURL'] = self.generate_resource_downloadURL(resource)
            current_resource['field'] = resource['attributesDescription']
            current_resource['attributes'] = tuple(resource['attributesDescription'])
            final_resource_list.append(current_resource)
        return final_resource_list

    def generate_resource_downloadURL(self, resource):
        downloadURL = resource.get('url').strip()
        if '' == downloadURL:
            downloadURL = None
        if isinstance(downloadURL, (str, unicode)):
            downloadURL = re.sub(r'\[\[/?REDACTED(-EX\sB\d)?\]\]', '', downloadURL)
            downloadURL = downloadURL.strip()
            if '' == downloadURL:
                downloadURL = None
            else:
                downloadURL = downloadURL.replace('http://[[REDACTED', '[[REDACTED')
                downloadURL = downloadURL.replace('http://http', 'http')
        else:
            # no se pudo conseguir downloadURL
            pass
        return downloadURL

    def get_ckan_datasets(self, org=None, with_private=True):
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

    def get_datasets_with_resources(self, packages):
        for i in range(0, len(packages)):
            j = 0
            for extra in packages[i]['extras']:
                if extra.get('key') == 'language':
                    if not isinstance(extra.get('value'), (unicode, str)):
                        # Solo puedo operar si value es una instancia de UNICODE o STR
                        # logger.warn('No fue posible renderizar el campo: \"Language\".') todo: logger?
                        pass
                    else:
                        language = []
                        try:
                            # intento convertir directamente el valor de
                            # Language a una lista.
                            language = json.loads(extra['value'])
                        except ValueError:
                            # La traduccion no es posible, limpiar y reintentar
                            if "{" or "}" in extra.get('value'):
                                lang = extra['value'].replace('{', '').replace('}', '').split(',')
                            else:
                                lang = extra.get('value')
                            if ',' in lang:
                                lang = lang.split(',')
                            else:
                                lang = [lang]
                            language = json.loads(lang)
                        packages[i]['extras'][j]['value'] = language
                j += 1
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
            # Obtengo el ckan.site_url para chequear la propiedad del recurso.
            ckan_site_url = config.get('ckan.site_url')
            try:
                for index, resource in enumerate(packages[i]['resources']):
                    resource = packages[i]['resources'][index]
                    if not resource.get("accessURL", None):
                        accessURL = os.path.join(ckan_site_url, 'dataset', packages[i]['id'], 'resource',
                                                 resource['id'])
                        resource.update({'accessURL': accessURL})
            except KeyError:
                pass
            ckan_host = ''
            try:
                ckan_host = re.match(
                    r'(?:http)s?:\/\/([\w][^\/=\s]+)\/?|(^w{3}[\.\w][^\/\=\s]{2,})\/?',
                    packages[i]['resources'][0]['url']).group(0)
            except Exception:
                pass
            # themes = gobar_helpers.safely_map(dict.get, packages[i]['groups'], 'name')
            # packages[i]['groups'] = themes
            try:
                packages[i]['author'] = {
                    'name': packages[i]['author'],
                    'mbox': packages[i]['author_email']
                }
            except KeyError:
                pass
            # tags = gobar_helpers.safely_map(dict.get, packages[i]['tags'], 'display_name')
            # packages[i]['tags'] = tags
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


class GobArApiController(GAApiController, ApiController):

    def _remove_extra_id_field(self, json_string):
        json_dict = json.loads(json_string)
        has_extra_id = False
        if 'result' in json_dict and 'fields' in json_dict['result']:
            for field in json_dict['result']['fields']:
                if 'id' in field and field['id'] == '_id':
                    has_extra_id = True
                    json_dict['result']['fields'].remove(field)
            if has_extra_id and 'records' in json_dict['result']:
                for record in json_dict['result']['records']:
                    if '_id' in record:
                        del record['_id']
        return json.dumps(json_dict)

    def action(self, logic_function, ver=None):
        default_response = super(GobArApiController, self).action(logic_function, ver)
        if logic_function == 'datastore_search':
            default_response = self._remove_extra_id_field(default_response)
        return default_response

    def status(self):
        context = {'model': model, 'session': model.Session}
        data_dict = {}

        status = logic.get_action('status_show')(context, data_dict)
        gobar_status = logic.get_action('gobar_status_show')(context, data_dict)
        status['gobar_artifacts'] = gobar_status

        return self._finish_ok(status)
