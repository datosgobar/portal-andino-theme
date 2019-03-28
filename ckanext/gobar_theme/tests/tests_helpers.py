# encoding: utf-8

import os
import json
import urllib2
from mock import patch
import ckan.tests.factories as factories
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino
import ckan.tests.helpers as helpers
import ckanext.gobar_theme.helpers as gobar_helpers
from ckanext.gobar_theme.tests.TestAndino import GobArConfigControllerForTest
from ckan.model import license
from pylons import config
from pylons import tmpl_context
from ckan.common import c
from paste.deploy.converters import asbool
import ckan.common


def before_search(self, search_params):
    pass


def package_search(context, data_dict):
    # sometimes context['schema'] is None
    schema = (context.get('schema') or logic.schema.default_package_search_schema())
    # put the extras back into the data_dict so that the search can
    # report needless parameters
    data_dict.update(data_dict.get('__extras', {}))
    data_dict.pop('__extras', None)

    model = context['model']
    session = context['session']
    user = context.get('user')

    # Move ext_ params to extras and remove them from the root of the search
    # params, so they don't cause and error
    data_dict['extras'] = data_dict.get('extras', {})
    for key in [key for key in data_dict.keys() if key.startswith('ext_')]:
        data_dict['extras'][key] = data_dict.pop(key)

    # the extension may have decided that it is not necessary to perform
    # the query
    abort = data_dict.get('abort_search', False)

    if data_dict.get('sort') in (None, 'rank'):
        data_dict['sort'] = 'score desc, metadata_modified desc'

    results = []
    if not abort:
        if asbool(data_dict.get('use_default_schema')):
            data_source = 'data_dict'
        else:
            data_source = 'validated_data_dict'
        data_dict.pop('use_default_schema', None)

        result_fl = data_dict.get('fl')
        if not result_fl:
            data_dict['fl'] = 'id {0}'.format(data_source)
        else:
            data_dict['fl'] = ' '.join(result_fl)

        # Remove before these hit solr FIXME: whitelist instead
        include_private = asbool(data_dict.pop('include_private', False))
        include_drafts = asbool(data_dict.pop('include_drafts', False))
        data_dict.setdefault('fq', '')
        if not include_private:
            data_dict['fq'] = '+capacity:public ' + data_dict['fq']
        if include_drafts:
            data_dict['fq'] += ' +state:(active OR draft)'

        # Pop these ones as Solr does not need them
        extras = data_dict.pop('extras', None)

        query = search.query_for(model.Package)
        query.run(data_dict, permission_labels=None)

        # Add them back so extensions can use them on after_search
        data_dict['extras'] = extras

        if result_fl:
            for package in query.results:
                if package.get('extras'):
                    package.update(package['extras'] )
                    package.pop('extras')
                results.append(package)
        else:
            for package in query.results:
                # get the package object
                package_dict = package.get(data_source)
                ## use data in search index if there
                if package_dict:
                    # the package_dict still needs translating when being viewed
                    package_dict = json.loads(package_dict)
                    results.append(package_dict)
                else:
                    pass

        count = query.count
        facets = query.facets
    else:
        count = 0
        facets = {}
        results = []

    search_results = {
        'count': count,
        'facets': facets,
        'results': results,
        'sort': data_dict['sort']
    }

    # create a lookup table of group name to title for all the groups and
    # organizations in the current search's facets.
    group_names = []
    for field_name in ('groups', 'organization'):
        group_names.extend(facets.get(field_name, {}).keys())

    groups = (session.query(model.Group.name, model.Group.title)
                    .filter(model.Group.name.in_(group_names))
                    .all()
              if group_names else [])
    group_titles_by_name = dict(groups)

    # Transform facets into a more useful data structure.
    restructured_facets = {}
    for key, value in facets.items():
        restructured_facets[key] = {
            'title': key,
            'items': []
        }
        for key_, value_ in value.items():
            new_facet_dict = {}
            new_facet_dict['name'] = key_
            if key in ('groups', 'organization'):
                display_name = group_titles_by_name.get(key_, key_)
                display_name = display_name if display_name and display_name.strip() else key_
                new_facet_dict['display_name'] = display_name
            elif key == 'license_id':
                license = model.Package.get_license_register().get(key_)
                if license:
                    new_facet_dict['display_name'] = license.title
                else:
                    new_facet_dict['display_name'] = key_
            else:
                new_facet_dict['display_name'] = key_
            new_facet_dict['count'] = value_
            restructured_facets[key]['items'].append(new_facet_dict)
    search_results['search_facets'] = restructured_facets

    # After extensions have had a chance to modify the facets, sort them by
    # display name.
    for facet in search_results['search_facets']:
        search_results['search_facets'][facet]['items'] = sorted(
            search_results['search_facets'][facet]['items'],
            key=lambda facet: facet['display_name'], reverse=True)

    return search_results


import ckan.logic as logic
import ckan.lib.search as search
import ckan


class TestHelpers(TestAndino.TestAndino):

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def setup(self):
        super(TestHelpers, self).setup()
        self.admin = factories.Sysadmin()


@patch("ckan.logic.action.get.package_search", package_search)
class TestOrganizationHelpers(TestHelpers):

    def __init__(self):
        super(TestOrganizationHelpers, self).__init__()

    def create_organization(self, name, parent=''):
        data_dict = {'name': name}
        if parent:
            data_dict['groups'] = [{'name': parent}]
        context = {'user': factories._get_action_user_name(data_dict)}
        data_dict.setdefault('type', 'organization')
        ckan.common.c = None
        tmpl_context = None
        return helpers.call_action('organization_create', context=context, **data_dict)

    def test_organization_can_be_created(self):
        # import pdb; pdb.set_trace()
        nt.assert_equals(self.create_organization('nombre').get('name'), 'nombre')

    def test_organization_shows_1_dataset(self):
        organization = self.create_organization('org')
        self.create_package_with_n_resources(1, {'owner_org': organization['id']})
        organizations_info = gobar_helpers.organizations_basic_info()
        nt.assert_equals(organizations_info[0].get('available_package_count'), 1)


class TestLicenseHelpers(TestHelpers):

    def load_licenses(self, url):
        # No usamos la URL que nos llega por parámetro porque queremos hardcodear el path del JSON
        script_dir = os.path.dirname(__file__)
        relative_path = 'tests_config/licenses.json'
        license_url = "file://{}".format(os.path.join(script_dir, relative_path))
        response = urllib2.urlopen(license_url)
        response_body = response.read()
        license_data = json.loads(response_body)
        self.licenses = [license.License(entity) for entity in license_data]

    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def __init__(self):
        super(TestLicenseHelpers, self).__init__()
        self.licenses = gobar_helpers.license_options()

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_license_options_returns_14_licenses(self):
        nt.assert_equals(len(self.licenses), 14)

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_legacy_license_ids_are_detected(self):
        pddl_license = None
        for license in self.licenses:
            if license.id == 'PDDL-1.0':
                pddl_license = license
        nt.assert_true(gobar_helpers.id_belongs_to_license('odc-pddl', pddl_license))

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_legacy_id_search_returns_correct_license(self):
        license = gobar_helpers.get_license('odc-pddl')
        nt.assert_equals(license.title, u'Open Data Commons Public Domain Dedication and Licence 1.0 (PDDL)')

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_license_title_search_returns_correct_title(self):
        nt.assert_equals(gobar_helpers.get_license_title('odc-pddl'),
                         u'Open Data Commons Public Domain Dedication and Licence 1.0 (PDDL)')
