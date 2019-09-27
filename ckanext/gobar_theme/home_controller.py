#!coding: utf-8
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
from ckan.common import c
from ckan.controllers.home import HomeController
from pylons import response

import ckanext.gobar_theme.helpers as gobar_helpers


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
            'q': '',
            'fq': 'home_featured:true',
            'rows': 500
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

    def view_about_section(self, title_or_slug):
        sections = gobar_helpers.get_theme_config('about.sections', [])

        for section in sections:
            if section.get('slug', '') == title_or_slug or section['title'] == title_or_slug:
                # la variable `section` contiene la sección buscada
                return base.render('section_view.html', extra_vars={'section': section})

        return base.abort(404, u'Sección no encontrada')


    def super_theme_taxonomy(self):
        response.content_type = 'application/json; charset=UTF-8'
        return base.render('home/super_theme_taxonomy.html')
