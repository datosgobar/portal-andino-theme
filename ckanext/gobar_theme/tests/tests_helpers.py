# encoding: utf-8

import os
import json
import urllib2
import nose.tools as nt
import ckan.tests.factories as factories
import ckanext.gobar_theme.helpers as gobar_helpers
from mock import patch
from ckan.model import license
from ckanext.gobar_theme.tests import TestAndino
from ckanext.gobar_theme.tests.TestAndino import get_test_theme_config
import ckanext.gobar_theme.tests.tools.organizations_manager as orgs_manager


class TestHelpers(TestAndino.TestAndino):

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def setup(self):
        super(TestHelpers, self).setup()
        self.admin = factories.Sysadmin()


@patch("ckan.logic.get_action", orgs_manager.get_action)
@patch("ckan.logic.action.get.package_search", orgs_manager.package_search)
@patch("ckan.lib.helpers.get_request_param", orgs_manager.get_request_param)
@patch("ckan.lib.dictization.model_dictize.group_dictize", orgs_manager.group_dictize)
class TestOrganizationHelpers(TestHelpers):

    def __init__(self):
        super(TestOrganizationHelpers, self).__init__()

    def test_organization_can_be_created(self):
        nt.assert_equals(orgs_manager.create_organization(name='nombre').get('name'), 'nombre')

    @patch("ckan.lib.helpers.get_facet_items_dict", orgs_manager.get_facet_items_dict)
    def test_organization_shows_1_dataset(self):
        organization = orgs_manager.create_organization(name='org')
        self.create_package_with_n_resources(1, {'owner_org': organization['id']})
        organizations_info = {item['name']: item for item in gobar_helpers.organizations_basic_info()}
        nt.assert_equals(organizations_info['org'].get('available_package_count'), 1)

    @patch("ckan.lib.helpers.get_facet_items_dict", orgs_manager.get_facet_items_dict_org_with_child)
    def test_organization_shows_2_datasets(self):
        father_organization = orgs_manager.create_organization(name='father')
        child_organization = orgs_manager.create_organization(name='child', parent='father')
        self.create_package_with_n_resources(1, {'name': 'one', 'owner_org': father_organization['id']})
        self.create_package_with_n_resources(1, {'name': 'two', 'owner_org': child_organization['id']})
        organizations_info = {item['name']: item for item in gobar_helpers.organizations_basic_info()}
        nt.assert_equals(organizations_info['father'].get('available_package_count'), 2)


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

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_license_options_returns_14_licenses(self):
        nt.assert_equals(len(self.licenses), 14)

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_legacy_license_ids_are_detected(self):
        pddl_license = None
        for license in self.licenses:
            if license.id == 'PDDL-1.0':
                pddl_license = license
        nt.assert_true(gobar_helpers.id_belongs_to_license('odc-pddl', pddl_license))

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_legacy_id_search_returns_correct_license(self):
        license = gobar_helpers.get_license('odc-pddl')
        nt.assert_equals(license.title, u'Open Data Commons Public Domain Dedication and Licence 1.0 (PDDL)')

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_license_title_search_returns_correct_title(self):
        nt.assert_equals(gobar_helpers.get_license_title('odc-pddl'),
                         u'Open Data Commons Public Domain Dedication and Licence 1.0 (PDDL)')
