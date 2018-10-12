#! coding: utf-8

from routes import url_for
from mock import patch
from mockredis import mock_strict_redis_client
from ckan.tests import helpers as helpers
import ckan.tests.factories as factories
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino

submit_and_follow = helpers.submit_and_follow


class TestDatasets(TestAndino.TestAndino):

    def __init__(self):
        super(TestDatasets, self).__init__()

    def setup(self):
        super(TestDatasets, self).setup()

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_check_created_dataset_note(self):
        self.create_package_with_n_resources(
            data_dict={'name': 'test', 'title': 'test_package', 'notes': 'this is my custom note'})
        pkg = helpers.call_action('package_show', name_or_id='test')
        nt.assert_equals('this is my custom note', pkg['notes'])

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_check_dataset_url_exists(self):
        dataset = self.create_package_with_n_resources(
            data_dict={'name': 'test', 'title': 'test_package', 'notes': 'this is my custom note'})
        bulk_process_url = url_for(controller='package', action='read', id=dataset.get("id"))
        self.generate_datajson()  # Al pedo, porque siempre se va a buscar la caché en el lugar normal, no /tmp
        result = self.app.get(url=bulk_process_url, status=200)
        nt.assert_true(result.status.endswith("200 OK"))

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_create_dataset_with_2_packages(self):
        pkg = self.create_package_with_n_resources(n=2, data_dict={'name': "test_package_with_resources"})
        nt.assert_equal(len(pkg['resources']), 2)

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_update_dataset_note(self):
        self.create_package_with_n_resources(
            data_dict={'name': 'test', 'title': 'test_package', 'notes': 'this is my custom note'})
        helpers.call_action('package_update', name='test', notes='this is my updated text')
        pkg = helpers.call_action('package_show', name_or_id='test')
        nt.assert_equals('this is my updated text', pkg['notes'])

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_create_package_with_one_resource_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms()
        nt.assert_equal(pkg.resources[0].url, u'http://example.com/resource')
        nt.assert_equal(pkg.state, 'active')

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_create_two_packages_with_one_resource_each_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms(dataset_name="ds_1", resource_url="http://1.com")
        nt.assert_equal(pkg.resources[0].url, u'http://1.com')
        pkg2 = self.create_package_with_one_resource_using_forms(dataset_name="ds_2", resource_url="http://2.com")
        nt.assert_equal(pkg2.resources[0].url, u'http://2.com')

    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_update_package_notes_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms(dataset_name="ds_1", resource_url="http://1.com")
        nt.assert_equal(pkg.resources[0].url, u'http://1.com')
        pkg = self.update_package_using_forms(pkg.name)
        nt.assert_equal(pkg.notes, u'New description')

    # @patch('redis.StrictRedis', mock_strict_redis_client)
    # def test_delete_dataset_using_forms_and_check_url_throws_404(self):
    #     error_thrown = False
    #     # pkg = self.create_package_with_one_resource_using_forms(dataset_name="ds_1")
    #     self.org = factories.Organization()
    #     pkg = factories.Dataset(name="ds_1", owner_org=self.org['id'])
    #     response = self.delete_package_using_forms("ds_1")
    #     # TODO: para colaboradores, está tirando error de permisos al submittear el form
    #     # TODO: para admins, está tirando error por un tema de organizaciones
    #     nt.assert_equal(200, response.status_int)
    #     url = url_for(controller='package', action='read', id=pkg.name)
    #     try:
    #         _, response = self.get_page_response(url, admin_required=True)
    #     except Exception:
    #         # Surge un AppError 404 tratando de conseguir el response; el dataset fue borrado y no funciona su URL
    #         error_thrown = True
    #     nt.assert_true(error_thrown)
