from mock import patch
from mockredis import mock_strict_redis_client
from routes import url_for
from ckan.tests import helpers as helpers
import ckan.tests.factories as factories
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino
from ckanext.gobar_theme.tests.TestAndino import GobArConfigControllerForTest

submit_and_follow = helpers.submit_and_follow


class TestConfiguration(TestAndino.TestAndino):

    def __init__(self):
        super(TestConfiguration, self).__init__()

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def setup(self):
        super(TestConfiguration, self).setup()
        self.admin = factories.Sysadmin()


class TestSeriesTiempoAr(TestConfiguration):

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


class TestGoogleDatasetSearch(TestConfiguration):

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_can_be_enabled(self):
        env, response = self.get_page_response('/configurar/google_dataset_search', admin_required=True)
        response = \
            self.edit_form_value(response, field_name='enable_structured_data', field_type='checkbox', value=True)

        form = response.forms['google-dataset-search']
        nt.assert_equals(form['enable_structured_data'].checked, True)


class TestGoogleTagManager(TestConfiguration):

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_id_can_be_configured(self):
        env, response = self.get_page_response('/configurar/google_tag_manager', admin_required=True)
        form = response.forms['google-tag-manager']
        # Chequeamos que el valor default sea utilizado
        nt.assert_equals(form['container-id'].value, "id-default")
        response = \
            self.edit_form_value(response, field_name='container-id', field_type='text', value="id-custom")

        form = response.forms['google-tag-manager']
        nt.assert_equals(form['container-id'].value, "id-custom")


class TestGoogleAnalytics(TestConfiguration):

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_id_can_be_configured(self):
        env, response = self.get_page_response('/configurar/google_analytics', admin_required=True)
        form = response.forms['google-analytics']
        # Chequeamos que el valor default sea utilizado
        nt.assert_equals(form['id'].value, "UA-101681828-1")
        response = \
            self.edit_form_value(response, field_name='id', field_type='text', value="id-custom")

        form = response.forms['google-analytics']
        nt.assert_equals(form['id'].value, "id-custom")
