#! coding: utf-8

import os
import ckan
import ckan.lib.search
from ckanext.gobar_theme.lib.datajson_actions import generate_new_cache_file, filter_dataset_fields, \
    get_datasets_with_resources, get_ckan_datasets, CACHE_DIRECTORY
from ckanext.gobar_theme.tests import TestAndino as TestAndino
from ckanext.gobar_theme.tests.TestAndino import get_test_theme_config
from ckanext.gobar_theme.tests.tools.organizations_manager import package_search, group_dictize, get_action
from ckanext.gobar_theme.tests.tools.datajson_manager import prepare_context_variable
import ckan.model as model
import tempfile
from ckan.tests import helpers as helpers
import nose.tools as nt

from mock import patch
from mockredis import mock_strict_redis_client


@patch("ckan.logic.get_action", get_action)
@patch("ckan.logic.action.get.package_search", package_search)
@patch("ckan.lib.dictization.model_dictize.group_dictize", group_dictize)
@patch('ckanext.gobar_theme.lib.datajson_actions.prepare_context_variable', prepare_context_variable)
class TestDatajsonGeneration(TestAndino.TestAndino):

    def __init__(self):
        super(TestDatajsonGeneration, self).__init__()

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def setup(self):
        super(TestDatajsonGeneration, self).setup()
        self.dataset = helpers.call_action('package_create', name='test_package', title='this is my custom title')

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def teardown(self):
        model.repo.rebuild_db()
        ckan.lib.search.clear_all()
        try:
            os.remove(self.TEST_CACHE_PATH)
        except OSError:
            # Se ejecutó un test que no requería crear el archivo
            pass

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def test_correct_search_results_for_dataset(self):
        self.create_package_with_n_resources(n=4, data_dict={'title': 'Un titulo 1', 'name': 'ds1'})
        self.create_package_with_n_resources(n=1, data_dict={'title': 'Un titulo 2', 'name': 'ds2'})
        datasets = filter_dataset_fields(get_datasets_with_resources(get_ckan_datasets()) or [])
        # Convierto la lista de datasets en un diccionario, usando el title como key y el resto del dataset como value
        datasets_dict = {}
        for ds in datasets:
            current_title = ds.pop('title')
            datasets_dict[current_title] = ds
        nt.assert_equal(len(datasets_dict.get('Un titulo 1').get('distribution')), 4)
        nt.assert_equal(len(datasets_dict.get('Un titulo 2').get('distribution')), 1)

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def test_datajson_cache_exists(self):
        file_descriptor, file_path = tempfile.mkstemp(suffix='.json', dir=CACHE_DIRECTORY)
        generate_new_cache_file(file_descriptor)
        os.rename(file_path, self.TEST_CACHE_PATH)
        nt.assert_true(os.path.isfile(self.TEST_CACHE_PATH))

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def test_datajson_contains_three_datasets(self):
        # Creo dos datasets aparte del creado en la función setup()
        self.create_package_with_n_resources(n=4, data_dict={'title': 'Un titulo 1', 'name': 'ds1'})
        self.create_package_with_n_resources(n=1, data_dict={'title': 'Un titulo 2', 'name': 'ds2'})
        datajson = self.generate_datajson(CACHE_DIRECTORY, self.TEST_CACHE_PATH)
        nt.assert_equal(len(datajson['dataset']), 3)

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_optional_dataset_fields_are_not_included_if_empty(self):
        optional_dataset_fields_names = ['source', 'language', 'spatial', 'quality', 'publisher', 'contactPoint',
                                         'theme', 'keyword', 'temporal', 'license']
        optional_resource_fields_names = ['mediaType', 'rights', 'description', 'field', 'format',
                                          'fileName', 'license', 'type']
        self.create_package_with_n_resources(n=1, data_dict={'title': 'Un titulo', 'name': 'ds1'})
        datajson = self.generate_datajson(CACHE_DIRECTORY, self.TEST_CACHE_PATH)
        dataset = datajson['dataset'][0]
        resource = dataset['distribution'][0]
        for name in optional_dataset_fields_names:
            nt.assert_true(name not in dataset.keys())
        for name in optional_resource_fields_names:
            nt.assert_true(name not in resource.keys())

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_catalog_data_is_in_datajson_and_title_is_correct(self):
        datajson = self.generate_datajson(CACHE_DIRECTORY, self.TEST_CACHE_PATH)
        nt.assert_equal(datajson['title'], u'Título del portal')

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_datajson_displays_resource_type(self):
        resources = [{'id': 'res1',
                      'title': 'resource:_title',
                      'resource_type': 'file',
                      'url': 'http://example.com/resource'}]
        data_dict = {
            'title': 'Un titulo', 'name': 'ds1', 'resources': resources}
        helpers.call_action('package_create', **data_dict)
        datajson = self.generate_datajson(CACHE_DIRECTORY, self.TEST_CACHE_PATH)
        distribution = datajson['dataset'][0]['distribution'][0]
        nt.assert_equal(distribution['type'], 'file')
