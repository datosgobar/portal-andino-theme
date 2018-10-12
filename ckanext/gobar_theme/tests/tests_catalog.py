#! coding: utf-8

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


class TestCatalog(TestAndino.TestAndino):

    def __init__(self):
        super(TestCatalog, self).__init__()

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def setup(self):
        ckan.plugins.load('example_iauthfunctions_v6_parent_auth_functions')
        super(TestCatalog, self).setup()
        self.admin = factories.Sysadmin()

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_edit_title_then_config_file_has_correct_values(self):
        _, response = self.get_page_response(url_for('/configurar/titulo'), admin_required=True)
        nt.assert_equals(response.forms['title-config']['site-title'].value, u'Título del portal')
        response = self.edit_form_value(response, 'title-config', 'site-title', u'Campo modificado')

        form = response.forms['title-config']
        nt.assert_equals(form['site-title'].value, u'Campo modificado')

        self.return_value_to_default('/configurar/titulo', 'title-config', 'site-title', u'Título del portal')
