#! coding: utf-8

import tempfile
import json
import os
from routes import url_for
from pylons.config import config
import sqlalchemy
import ckan
import ckan.lib.search
import ckan.tests.factories as factories
from ckan.tests import helpers as helpers
import ckan.model as model
from ckanext.gobar_theme.lib.datajson_actions import generate_new_cache_file

submit_and_follow = helpers.submit_and_follow


def create_package_with_n_resources(n=0, data_dict={}):
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


def get_page_response(app, url, admin_required=False):
    '''
    :param app: app brindada por un Test
    :param url: url a la cual se deberá acceder
    :param admin_required: será True en caso de que se quiera realizar una operación que necesite un admin
    :return: env relacionado al usuario utilizado (sólo para helpers) y el response correspondiente a la url recibida
    '''
    if admin_required:
        user = factories.Sysadmin()
    else:
        user = factories.User()
    env = {'REMOTE_USER': user['name'].encode('ascii')}
    response = app.get(url=url_for(url), extra_environ=env)
    if '30' in response.status:
        # Hubo una redirección; necesitamos la URL final para obtener sus forms
        response = app.get(url=url(response.location), extra_environ=env)
    return env, response


# --- Datasets --- #


def create_package_with_one_resource_using_forms(test, dataset_name=u'package-with-one-resource',
                                                 resource_url=u'http://example.com/resource'):
    app = test.get_app()
    env, response = get_page_response(app, '/dataset/new')

    form = response.forms['dataset-edit']
    form['name'] = dataset_name
    response = submit_and_follow(app, form, env, 'save')

    form = response.forms['resource-edit']
    form['url'] = resource_url
    submit_and_follow(app, form, env, 'save', 'go-metadata')
    return model.Package.by_name(dataset_name)


def delete_package_using_forms(test, dataset_name):
    app = test.get_app()
    env, response = get_page_response(app, url_for('/dataset/delete/{0}'.format(dataset_name)))
    form = response.forms['confirm-dataset-delete-form']
    response = submit_and_follow(app, form, env, 'delete')
    return response


# --- Resources --- #


def create_resource_using_forms(test, dataset_name, resource_name=u'resource'):
    env, response = get_page_response(app, str('/dataset/new_resource/%s' % dataset_name))

    form = response.forms['resource-edit']
    form['url'] = u'http://example.com/resource'
    form['name'] = resource_name
    submit_and_follow(app, form, env, 'save', 'go-dataset-complete')
    return model.Resource.by_name(resource_name)


def delete_resource_using_forms(test, dataset_name, resource_id):
    app = test.get_app()
    env, response = get_page_response(
        app, url_for('/dataset/{0}/resource_delete/{1}'.format(dataset_name, resource_id)))

    form = response.forms['confirm-resource-delete-form']
    try:
        response = submit_and_follow(app, form, env, 'delete')
    except (sqlalchemy.exc.ProgrammingError):
        # Error subiendo al datastore
        # TODO: Consultar
        pass
    return response


# --- Datajson --- #


def generate_datajson(cache_directory='/tmp/', cache_filename='/tmp/datajson_cache_test.json'):
    file_descriptor, file_path = tempfile.mkstemp(suffix='.json', dir=cache_directory)
    generate_new_cache_file(file_descriptor)
    os.rename(file_path, cache_filename)
    with open(cache_filename, 'r+') as file:
        return json.loads(file.read())


# --- Catalog --- #


def return_value_to_default(app, url, form_name, field_name, value):
    # Restauro la información default, tal y como estaba antes de testear
    _, response = get_page_response(app, url_for(url), admin_required=True)
    edit_form_value(app, response, form_name, field_name, value)


def edit_form_value(app, response, form_name, field_name, value=u'Campo modificado'):
    admin = factories.Sysadmin()
    form = response.forms[form_name]
    form[field_name].value = value
    env = {'REMOTE_USER': admin['name'].encode('ascii')}
    try:
        response = submit_and_follow(app, form, env, 'save', value="config-form")
    except Exception:
        # Trató de encolar una tarea
        pass
    return response
