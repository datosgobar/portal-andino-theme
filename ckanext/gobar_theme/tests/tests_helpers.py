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


class TestHelpers(TestAndino.TestAndino):

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def setup(self):
        super(TestHelpers, self).setup()
        self.admin = factories.Sysadmin()


class TestLicenseHelpers(TestHelpers):

    def load_licenses(self, url):
        # No usamos la URL que nos llega por parámetro porque queremos hardcodear el path del JSON
        script_dir = os.path.dirname(__file__)
        relative_path = 'tests_config/licenses.json'
        license_url = "file://{}".format(os.path.join(script_dir, relative_path))
        response = urllib2.urlopen(license_url)
        response_body = response.read()
        license_data = json.loads(response_body)
        license_register = license.LicenseRegister()
        license_register._create_license_list(license_data, '')

    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def __init__(self):
        super(TestLicenseHelpers, self).__init__()
        self.licenses = gobar_helpers.license_options()

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('ckan.model.license.LicenseRegister.load_licenses', load_licenses)
    def test_license_options_returns_1_licenses(self):
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
