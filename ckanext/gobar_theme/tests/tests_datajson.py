#! coding: utf-8

import os
import ckan
import ckan.lib.search
from ckanext.gobar_theme.lib.datajson_actions import generate_new_cache_file, filter_dataset_fields, \
    get_datasets_with_resources, get_ckan_datasets, CACHE_DIRECTORY, CACHE_FILENAME
from ckanext.gobar_theme.tests import TestAndino as TestAndino
from ckanext.gobar_theme.tests.TestAndino import GobArConfigControllerForTest
import ckan.model as model
import tempfile
from ckan.tests import helpers as helpers
import nose.tools as nt

from mock import patch
from mockredis import mock_strict_redis_client


class TestDatajsonGeneration(TestAndino.TestAndino):

    def __init__(self):
        super(TestDatajsonGeneration, self).__init__()

    def setup(self):
        super(TestDatajsonGeneration, self).setup()
        self.dataset = helpers.call_action('package_create', name='test_package', title='this is my custom title')

    def teardown(self):
        model.repo.rebuild_db()
        ckan.lib.search.clear_all()
        try:
            os.remove(CACHE_FILENAME)
        except OSError:
            # Se ejecutó un test que no requería crear el archivo
            pass

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
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
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_datajson_cache_exists(self):
        file_descriptor, file_path = tempfile.mkstemp(suffix='.json', dir=CACHE_DIRECTORY)
        generate_new_cache_file(file_descriptor)
        os.rename(file_path, CACHE_FILENAME)
        nt.assert_true(os.path.isfile(CACHE_FILENAME))

    @patch('redis.StrictRedis', mock_strict_redis_client)
    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    def test_datajson_contains_three_datasets(self):
        # Creo dos datasets aparte del creado en la función setup()
        self.create_package_with_n_resources(n=4, data_dict={'title': 'Un titulo 1', 'name': 'ds1'})
        self.create_package_with_n_resources(n=1, data_dict={'title': 'Un titulo 2', 'name': 'ds2'})
        datajson = self.generate_datajson(CACHE_DIRECTORY, CACHE_FILENAME)
        nt.assert_equal(len(datajson['dataset']), 3)

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_optional_dataset_fields_are_not_included_if_empty(self):
        optional_dataset_fields_names = ['source', 'language', 'spatial', 'quality', 'publisher', 'contactPoint',
                                         'theme', 'modified', 'landingPage', 'keyword', 'temporal', 'license']
        optional_resource_fields_names = ['mediaType', 'rights', 'description', 'field', 'modified', 'format',
                                          'fileName', 'license', 'type']
        self.create_package_with_n_resources(n=1, data_dict={'title': 'Un titulo', 'name': 'ds1'})
        datajson = self.generate_datajson(CACHE_DIRECTORY, CACHE_FILENAME)
        dataset = datajson['dataset'][0]
        resource = dataset['distribution'][0]
        for name in optional_dataset_fields_names:
            nt.assert_true(name not in dataset.keys() or dataset[name])
        for name in optional_resource_fields_names:
            nt.assert_true(name not in resource.keys() or resource[name])

    @patch('ckanext.gobar_theme.helpers.GobArConfigController', GobArConfigControllerForTest)
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def test_catalog_data_is_in_datajson_and_title_is_correct(self):
        datajson = self.generate_datajson(CACHE_DIRECTORY, CACHE_FILENAME)
        nt.assert_equal(datajson['title'], u'Título del portal')
