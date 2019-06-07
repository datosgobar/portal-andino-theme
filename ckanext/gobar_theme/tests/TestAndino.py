#! coding: utf-8

import json
import logging
import os
import tempfile

import ckan
import ckan.lib.search
import ckan.logic as logic
import ckan.model as model
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import sqlalchemy
from mock import patch
from routes import url_for

from ckanext.gobar_theme.config_controller import ThemeConfig
from ckanext.gobar_theme.lib.datajson_actions import CACHE_DIRECTORY
from ckanext.gobar_theme.lib.datajson_actions import generate_new_cache_file
from ckanext.gobar_theme.tests.tools.datajson_manager import enqueue_update_datajson_cache_tasks
from ckanext.gobar_theme.tests.tools.organizations_manager import package_search, group_dictize, create_organization, \
    get_action

logger = logging.getLogger(__name__)
submit_and_follow = helpers.submit_and_follow
parse_params = logic.parse_params


def get_test_theme_config(_=None):
    return ThemeConfig(CACHE_DIRECTORY + "test_settings.json")


@patch("ckan.logic.get_action", get_action)
@patch("ckan.logic.action.get.package_search", package_search)
@patch("ckan.lib.dictization.model_dictize.group_dictize", group_dictize)
class TestAndino(helpers.FunctionalTestBase):

    def __init__(self):
        self.app = self._get_test_app()
        self.org = None
        self.TEST_CACHE_PATH = CACHE_DIRECTORY + "datajson_cache_backup.json"

    @patch("ckan.logic.action.get.package_search", package_search)
    @patch("ckan.lib.dictization.model_dictize.group_dictize", group_dictize)
    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    def setup(self):
        super(TestAndino, self).setup()
        self.org = create_organization(name='organizacion')

    @classmethod
    def setup_class(cls):
        super(TestAndino, cls).setup_class()
        # Creo un nuevo settings.json para ser usado durante el testeo
        cls.create_or_update_settings_json_file()

    @classmethod
    def teardown_class(cls):
        super(TestAndino, cls).teardown_class()
        model.repo.rebuild_db()
        ckan.lib.search.clear_all()
        try:
            os.remove(CACHE_DIRECTORY + "datajson_cache_backup.json")
        except OSError:
            # No se creó una caché de testeo
            pass

    @staticmethod
    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def create_or_update_settings_json_file():
        # Creo un nuevo settings.json, o lo actualizo en caso de que ya exista, para ser usado durante el testeo
        script_dir = os.path.dirname(__file__)
        relative_path = 'tests_config/default.json.j2'
        complete_path = os.path.join(script_dir, relative_path)
        with open(CACHE_DIRECTORY + "test_settings.json", "w+") as test_settings, open(complete_path, 'r+') as original:
            test_settings.write(original.read())

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def create_package_with_n_resources(self, n=0, data_dict={}):
        '''
        :param n: cantidad de recursos a crear (ninguno por default)
        :param data_dict: campos opcionales pertenecientes al dataset cuyos datos se quieren proveer (no utilizar campos
            cuyos valores contengan tildes u otros caracteres que provoquen errores por UnicodeDecode.)
        :return: dataset con n recursos
        '''
        resources_list = []
        for i in range(n):
            resources_list.append({'url': 'http://test.com/', 'custom_resource_text': 'my custom resource #%d' % i})
        data_dict['resources'] = resources_list
        if 'name' not in data_dict.keys():
            data_dict['name'] = 'test_package'
        return helpers.call_action('package_create', **data_dict)

    # ------ Methods with factories ------ #

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.lib.datajson_actions.enqueue_update_datajson_cache_tasks',
           enqueue_update_datajson_cache_tasks)
    def get_page_response(self, url, admin_required=False):
        '''
        :param url: url a la cual se deberá acceder
        :param admin_required: deberá ser True en caso de que se quiera realizar una operación que necesite un admin
        :return: env relacionado al usuario utilizado, y el response correspondiente a la url recibida
        '''
        if admin_required:
            user = factories.Sysadmin()
        else:
            user = factories.User()
            # Los usuarios colaboradores requieren una organización para manipular datasets
            self.org['users'].append(user)
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        page_url = url_for(url)
        response = self.app.get(url=page_url, extra_environ=env)
        if '30' in response.status:
            # Hubo una redirección; necesitamos la URL final para obtener sus forms
            response = self.app.get(url=url(response.location), extra_environ=env)
        return env, response

    # --- Datasets --- #

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def create_package_with_one_resource_using_forms(self, dataset_name=u'package-with-one-resource',
                                                     resource_url=u'http://example.com/resource',
                                                     data_dict={},
                                                     draft=False):
        env, response = self.get_page_response('/dataset/new')
        form = response.forms['dataset-edit']
        form['name'] = dataset_name
        self.fill_form_using_data_dict(form, data_dict)
        response = submit_and_follow(self.app, form, env, 'save', 'continue')

        form = response.forms['resource-edit']
        form['url'] = resource_url
        button_value = 'save-draft' if draft else 'go-metadata'
        submit_and_follow(self.app, form, env, 'save', button_value)
        return model.Package.by_name(dataset_name)

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def update_package_using_forms(self, pkg, data_dict={}):
        dataset_name = pkg.name
        dataset_is_draft = pkg.state == 'draft'
        env, response = self.get_page_response('/dataset/edit/{0}'.format(dataset_name))
        form = response.forms['dataset-edit']
        form['notes'] = u'New description'
        self.fill_form_using_data_dict(form, data_dict)
        button_value = 'go-metadata' if dataset_is_draft else 'continue'
        submit_and_follow(self.app, form, env, 'save', button_value)
        return model.Package.by_name(dataset_name)

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def delete_package_using_forms(self, dataset_name):
        env, response = self.get_page_response(url_for('/dataset/delete/{0}'.format(dataset_name)), admin_required=True)
        form = response.forms['confirm-dataset-delete-form']
        response = submit_and_follow(self.app, form, env, 'delete')
        return response

    def fill_form_using_data_dict(self, form, data_dict):
        for key, value in data_dict:
            try:
                form[key] = value
            except KeyError:
                logger.warning("Se está pasando un parámetro incorrecto en un test de edición de datasets.")

    # --- Resources --- #

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def create_resource_using_forms(self, dataset_name, resource_name=u'resource'):
        env, response = self.get_page_response(str('/dataset/new_resource/%s' % dataset_name))
        form = response.forms['resource-edit']
        form['url'] = u'http://example.com/resource'
        form['name'] = resource_name
        submit_and_follow(self.app, form, env, 'save', 'go-dataset-complete')
        return model.Resource.by_name(resource_name)

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def delete_resource_using_forms(self, dataset_name, resource_id):
        url = url_for('/dataset/{0}/resource_delete/{1}'.format(dataset_name, resource_id))
        env, response = self.get_page_response(url)
        form = response.forms['confirm-resource-delete-form']
        try:
            response = submit_and_follow(self.app, form, env, 'delete')
        except sqlalchemy.exc.ProgrammingError:
            # Error subiendo al datastore
            pass
        return response

    # --- Datajson --- #

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def generate_datajson(self, cache_directory='/tmp/', cache_filename='/tmp/datajson_cache_test.json'):
        file_descriptor, file_path = tempfile.mkstemp(suffix='.json', dir=cache_directory)
        generate_new_cache_file(file_descriptor)
        os.rename(file_path, cache_filename)
        with open(cache_filename, 'r+') as file:
            return json.loads(file.read())

    # --- Portal --- #

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def return_value_to_default(self, url, form_name, field_name, value):
        # Restauro la información default, tal y como estaba antes de testear
        _, response = self.get_page_response(url_for(url), admin_required=True)
        self.edit_form_value(response, form_name, field_name, value)

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def edit_form_value(self, response, form_id=None, field_name=None, field_type='text', value=u'Campo modificado'):  # TODO: borrar y usar la nueva función en su lugar
        admin = factories.Sysadmin()
        if form_id:
            form = response.forms[form_id]
        else:
            # El form a buscar no tiene un id bajo el cual buscarlo
            form = response.forms[0]
        if field_type == 'text':
            form[field_name].value = value
        elif field_type == 'checkbox':
            form[field_name].checked = value
        env = {'REMOTE_USER': admin['name'].encode('ascii')}
        try:
            response = submit_and_follow(self.app, form, env, 'save', value="config-form")
        except Exception:
            # Trató de encolar una tarea
            pass
        return response

    @patch('ckanext.gobar_theme.helpers.ThemeConfig', get_test_theme_config)
    @patch('ckanext.gobar_theme.config_controller.ThemeConfig', get_test_theme_config)
    def edit_form_values(self, response, form_id=None, data_dict={}):
        admin = factories.Sysadmin()
        if form_id:
            form = response.forms[form_id]
        else:
            # El form a buscar no tiene un id bajo el cual buscarlo
            form = response.forms[0]
        for element in data_dict:
            if element.get('field_type') == 'text':
                form[element.get('field_name')].value = element.get('value')  # TODO: mejorar sección antes de mergear
            elif element.get('field_type') == 'checkbox':
                form[element.get('field_name')].checked = element.get('value')
        env = {'REMOTE_USER': admin['name'].encode('ascii')}
        try:
            response = submit_and_follow(self.app, form, env, 'save', value="config-form")
        except Exception:
            # Trató de encolar una tarea
            pass
        return response

