from mock import patch
from mockredis import mock_strict_redis_client
from routes import url_for
from ckan.tests import helpers as helpers
import ckan.tests.factories as factories
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino
from ckanext.gobar_theme.tests.TestAndino import GobArConfigControllerForTest

submit_and_follow = helpers.submit_and_follow


class TestSeriesTiempoAr(TestAndino.TestAndino):

    def __init__(self):
        super(TestSeriesTiempoAr, self).__init__()

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def setup(self):
        super(TestSeriesTiempoAr, self).setup()
        self.admin = factories.Sysadmin()

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_series_plugin_can_be_configured(self):
        _, response = self.get_page_response(url_for('/configurar/series'), admin_required=True)
        forms = response.forms
        nt.assert_true(isinstance(forms[0]['featured'].value, basestring))

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_url_exists(self):
        _, response = self.get_page_response(url_for('/series/api'), admin_required=True)
        nt.assert_equals(response.status_int, 200)
