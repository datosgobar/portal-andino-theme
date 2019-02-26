from mock import patch
from mockredis import mock_strict_redis_client
import ckan.tests.factories as factories
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino
import ckanext.gobar_theme.helpers as gobar_helpers
from ckanext.gobar_theme.tests.TestAndino import GobArConfigControllerForTest
from ckan.model import license


class TestHelpers(TestAndino.TestAndino):

    def __init__(self):
        super(TestHelpers, self).__init__()

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def setup(self):
        super(TestHelpers, self).setup()
        self.admin = factories.Sysadmin()


class TestLicenseHelpers(TestHelpers):

    def __init__(self):
        super(TestLicenseHelpers, self).__init__()
        licenses_json = [
            {
                "id": "PDDL-1.0",
                "legacy_ids": ["ODC-PDDL-1.0", "odc-pddl"],
                "title": "Open Data Commons Public Domain Dedication and Licence 1.0 (PDDL)",
                "url": "https://opendefinition.org/licenses/odc-pddl"
            },
            {
                "id": "ODbL-1.0",
                "legacy_ids": ["odc-odbl"],
                "title": "Open Data Commons Open Database License 1.0 (ODbL)",
                "url": "https://opendefinition.org/licenses/odc-odbl"
            }
        ]
        self.licenses = [license.License(entity) for entity in licenses_json]

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_license_options_returns_2_licenses(self):
        nt.assert_equals(len(self.licenses), 2)

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_legacy_license_ids_are_detected(self):
        pddl_license = None
        for license in self.licenses:
            if license.id == 'PDDL-1.0':
                pddl_license = license
        nt.assert_true(gobar_helpers.id_belongs_to_license('odc-pddl', pddl_license))

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_legacy_id_search_returns_correct_license(self):
        license = gobar_helpers.get_license('odc-pddl')
        nt.assert_equals(license.title, u'Open Data Commons Public Domain Dedication and Licence 1.0 (PDDL)')

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_license_title_search_returns_correct_title(self):
        nt.assert_equals(gobar_helpers.get_license_title('odc-pddl'),
                         u'Open Data Commons Public Domain Dedication and Licence 1.0 (PDDL)')
