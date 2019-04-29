#! coding: utf-8

from routes import url_for
from mock import patch
from mockredis import mock_strict_redis_client
from ckan.tests import helpers as helpers
import nose.tools as nt
from ckanext.gobar_theme.tests import TestAndino
from ckanext.gobar_theme.tests.TestAndino import get_test_theme_config

submit_and_follow = helpers.submit_and_follow


@patch('redis.StrictRedis', mock_strict_redis_client)
@patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
class TestDatasets(TestAndino.TestAndino):

    def __init__(self):
        super(TestDatasets, self).__init__()

    def setup(self):
        super(TestDatasets, self).setup()

    def test_check_created_dataset_note(self):
        self.create_package_with_n_resources(
            data_dict={'name': 'test', 'title': 'test_package', 'notes': 'this is my custom note'})
        pkg = helpers.call_action('package_show', name_or_id='test')
        nt.assert_equals('this is my custom note', pkg['notes'])

    def test_check_dataset_url_exists(self):
        dataset = self.create_package_with_n_resources(
            data_dict={'name': 'test', 'title': 'test_package', 'notes': 'this is my custom note'})
        bulk_process_url = url_for(controller='package', action='read', id=dataset.get("id"))
        result = self.app.get(url=bulk_process_url, status=200)
        nt.assert_true(result.status.endswith("200 OK"))

    def test_create_dataset_with_2_packages(self):
        pkg = self.create_package_with_n_resources(n=2, data_dict={'name': "test_package_with_resources"})
        nt.assert_equal(len(pkg['resources']), 2)

    def test_update_dataset_note(self):
        self.create_package_with_n_resources(
            data_dict={'name': 'test', 'title': 'test_package', 'notes': 'this is my custom note'})
        helpers.call_action('package_update', name='test', notes='this is my updated text')
        pkg = helpers.call_action('package_show', name_or_id='test')
        nt.assert_equals('this is my updated text', pkg['notes'])

    def test_create_package_with_one_resource_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms()
        nt.assert_equal(pkg.resources[0].url, u'http://example.com/resource')
        nt.assert_equal(pkg.state, 'active')

    def test_create_two_packages_with_one_resource_each_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms(dataset_name="ds_1", resource_url="http://1.com")
        nt.assert_equal(pkg.resources[0].url, u'http://1.com')
        pkg2 = self.create_package_with_one_resource_using_forms(dataset_name="ds_2", resource_url="http://2.com")
        nt.assert_equal(pkg2.resources[0].url, u'http://2.com')

    def test_update_package_notes_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms(dataset_name="ds_1", resource_url="http://1.com")
        nt.assert_equal(pkg.resources[0].url, u'http://1.com')
        pkg = self.update_package_using_forms(pkg)
        nt.assert_equal(pkg.notes, u'New description')

    def test_create_draft_dataset_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms(dataset_name="ds_1", resource_url="http://1.com",
                                                                draft=True)
        nt.assert_equal(pkg.state, 'draft')

    def test_publish_draft_dataset_using_forms(self):
        pkg = self.create_package_with_one_resource_using_forms(dataset_name="ds_1", resource_url="http://1.com")
        pkg = self.update_package_using_forms(pkg)
        nt.assert_equals(pkg.state, 'active')
