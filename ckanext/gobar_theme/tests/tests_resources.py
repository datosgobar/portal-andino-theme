#! coding: utf-8

from routes import url_for
from ckan.tests import helpers as helpers
import ckan.tests.factories as factories
import sqlalchemy
import nose.tools as nt
from mock import patch
from mockredis import mock_strict_redis_client
from ckanext.gobar_theme.lib.datajson_actions import CACHE_DIRECTORY
from ckanext.gobar_theme.tests import TestAndino
from ckanext.gobar_theme.tests.TestAndino import get_test_theme_config
from ckanext.gobar_theme.tests.tools.organizations_manager import package_search, group_dictize

submit_and_follow = helpers.submit_and_follow


@patch("ckan.logic.action.get.package_search", package_search)
@patch("ckan.lib.dictization.model_dictize.group_dictize", group_dictize)
class TestResources(TestAndino.TestAndino):

    def __init__(self):
        super(TestResources, self).__init__()

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def setup(self):
        super(TestResources, self).setup()
        self.dataset = self.create_package_with_n_resources(
            0, data_dict={'name': 'test', 'title': 'test_package', 'notes': 'this is my custom note'})
        self.resource = helpers.call_action(
            'resource_create', package_id=self.dataset['id'], name='test-resource', url='http://resource.create/')
        self.resource_id = self.resource.get('id')

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def test_check_created_resource_has_url(self):
        res = helpers.call_action('resource_show', id=self.resource_id)
        nt.assert_equals('http://resource.create/', res['url'])

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def test_update_resource_url(self):
        helpers.call_action('resource_update', id=self.resource_id, url='http://resource.update/')
        res = helpers.call_action('resource_show', id=self.resource_id)
        nt.assert_equals('http://resource.update/', res['url'])

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.lib.datajson_actions.CACHE_FILENAME', CACHE_DIRECTORY + "datajson_cache_backup.json")
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_check_resource_url_exists(self):
        _, response = self.get_page_response(
            url_for(controller='package', action='resource_read', id=self.dataset['id'], resource_id=self.resource_id))
        nt.assert_true(response.status.endswith("200 OK"))

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_create_resource_using_forms(self):
        dataset = factories.Dataset()
        res = self.create_resource_using_forms(dataset['id'], "resource")
        nt.assert_equal(res.url, u'http://example.com/resource')

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_delete_resource_using_forms(self):
        error_thrown = False
        dataset = factories.Dataset()
        res = self.create_resource_using_forms(dataset['id'], "resource")

        url = url_for('/dataset/{0}/resource_delete/{1}'.format(dataset['id'], res.id))

        user = factories.User()
        org = factories.Organization()
        # Los usuarios colaboradores requieren una organización para manipular datasets
        org['users'].append(user)
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        page_url = url_for(url)
        response = self.app.get(url=page_url, extra_environ=env)
        if '30' in response.status:
            # Hubo una redirección; necesitamos la URL final para obtener sus forms
            response = self.app.get(url=url(response.location), extra_environ=env)

        form = response.forms['confirm-resource-delete-form']
        try:
            response = submit_and_follow(self.app, form, env, 'delete')
        except sqlalchemy.exc.ProgrammingError:
            # Error subiendo al datastore
            pass

        nt.assert_equal(200, response.status_int)
        try:
            _, response = self.get_page_response(
                url_for(controller='package', action='resource_read', id=dataset['id'], resource_id="resource"))
        except Exception:
            # Surge un AppError 404 tratando de conseguir el response; el recurso fue borrado y no funciona su URL
            error_thrown = True
        nt.assert_true(error_thrown)
