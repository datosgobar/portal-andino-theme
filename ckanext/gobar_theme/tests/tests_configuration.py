from mock import patch
from mockredis import mock_strict_redis_client
from routes import url_for
from ckan.tests import helpers as helpers
import ckan.tests.factories as factories
import nose.tools as nt
import subprocess
from crontab import CronTab
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


class TestDatapusherCommands(TestConfiguration):

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_cron_job_is_created(self):
        # Creo el cron job
        env, response = self.get_page_response('/configurar/datapusher', admin_required=True)
        self.edit_form_value(response, field_name=None, field_type=None, value=True)
        # Vuelvo a crear el cron job, reemplazando el anterior
        env, response = self.get_page_response('/configurar/datapusher', admin_required=True)
        self.edit_form_value(response, field_name=None, field_type=None, value=True)

        import logging
        logger = logging.getLogger(__name__)
        logger.info("Contenido de crontab: {}".format(subprocess.check_output(
            'crontab -u www-data -l', shell=True).strip()))
        amount_of_datapusher_jobs = subprocess.check_output(
            'crontab -u www-data -l | grep "datapusher - submit_all" | wc -l', shell=True).strip()
        nt.assert_equals(amount_of_datapusher_jobs, "1")
