# encoding: utf-8

import os
import json
import urllib2
from mock import patch
import ckan.tests.factories as factories
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino
import ckanext.gobar_theme.helpers as gobar_helpers
from ckanext.gobar_theme.tests.TestAndino import GobArConfigControllerForTest
from ckan.model import license
from pylons.config import config
from ckanapi import RemoteCKAN, LocalCKAN


class TestHelpers(TestAndino.TestAndino):

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def setup(self):
        super(TestHelpers, self).setup()
        self.admin = factories.Sysadmin()


class TestOrganizationHelpers(TestHelpers):

    def __init__(self):
        super(TestOrganizationHelpers, self).__init__()

    def create_organization(self, name, parent=''):
        # env, response = self.get_page_response('/organization/new', admin_required=True)
        # form = response.forms['organization-edit-form']
        # data_dict = {{'field_name': 'title', 'field_type': 'text', 'value': name},
        #              {'field_name': 'hierarchy', 'field_type': 'text', 'value': parent}}
        # response = \
        #     self.edit_form_values(response, field_name='title', field_type='text', value="id-custom")
        # form = response.forms['google-tag-manager']
        # nt.assert_equals(form['container-id'].value, "id-custom")

        lc = LocalCKAN()
        site_user = lc._get_action('get_site_user')({'ignore_auth': True}, ())
        apikey = site_user.get('apikey')
        site_url = gobar_helpers.search_for_value_in_config_file('ckan.site_url') or 'http://localhost'
        portal = RemoteCKAN(site_url, apikey=apikey)
        organization = {'name': name}
        if parent:
            organization['groups'] = [{'name': parent}]
        return portal.call_action('organization_create', data_dict=organization)

    def test_organization_can_be_created(self):
        nt.assert_equals(self.create_organization('nombre'), 'nombre')

    def test_organization_shows_1_dataset(self):
        organization = self.create_organization('org')
        self.create_package_with_n_resources(1, {'owner_org': organization})
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
