#! coding: utf-8

from mock import patch
from mockredis import mock_strict_redis_client, mock_redis_client
from routes import url_for
from ckan.tests import helpers as helpers
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino

submit_and_follow = helpers.submit_and_follow


class TestCatalog(TestAndino.TestAndino):

    def __init__(self):
        super(TestCatalog, self).__init__()

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def setup(self):
        super(TestCatalog, self).setup()

    def teardown(self):
        _, response = self.get_page_response(url_for('/configurar/titulo'), admin_required=True)
        self.edit_form_value(
            response, form_id='title-config', field_name='site-title', value=u'Título del portal')

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('redis.Redis', mock_redis_client)
    @patch('datajson_actions.jobs', autospec=True)
    def test_edit_title_then_config_file_has_correct_values(self, mock_job):
        _, response = self.get_page_response(url_for('/configurar/titulo'), admin_required=True)
        nt.assert_equals(response.forms['title-config']['site-title'].value, u'Título del portal')
        response = self.edit_form_value(
            response, form_id='title-config', field_name='site-title', value=u'Campo modificado')

        form = response.forms['title-config']
        nt.assert_equals(form['site-title'].value, u'Campo modificado')
