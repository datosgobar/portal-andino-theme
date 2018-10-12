from mock import patch
from mockredis import mock_strict_redis_client
from routes import url_for
import ckan
import ckan.lib.search
from ckan.tests import helpers as helpers
import ckan.tests.factories as factories
import nose.tools as nt
# import ckanext.gobar_theme.tests.test_helpers as test_helpers
from ckanext.gobar_theme.tests import TestAndino

submit_and_follow = helpers.submit_and_follow


class TestSeriesTiempoAr(TestAndino.TestAndino):

    def __init__(self):
        super(TestSeriesTiempoAr, self).__init__()

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def setup(self):
        ckan.plugins.load('example_iauthfunctions_v6_parent_auth_functions')
        super(TestSeriesTiempoAr, self).setup()
        self.admin = factories.Sysadmin()

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_enable_series(self):
        _, response = self.get_page_response(url_for('/configurar/series'), admin_required=True)
        forms = response.forms
        nt.assert_true(isinstance(forms[0]['featured'].value, basestring))
