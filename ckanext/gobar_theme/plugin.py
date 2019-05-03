#! coding: utf-8
import inspect

import ckan.lib.helpers as ckan_helpers
import ckan.plugins as plugins
import ckan.plugins.interfaces as interfaces
from ckan.plugins import toolkit
from ckan.model.package import Package
from ckan.model.resource import Resource
from ckan.plugins import implements, IRoutes

import ckanext.gobar_theme.actions as gobar_actions
import ckanext.gobar_theme.helpers as gobar_helpers
import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
import ckanext.gobar_theme.routing as gobar_routes
from ckanext import constants
from ckanext.gobar_theme.lib import cache_actions
from ckanext.gobar_theme.theme_config import ThemeConfig
from ckanext.gobar_theme.uploader import GobArThemeResourceUploader


class Gobar_ThemePlugin(plugins.SingletonPlugin):
    implements(plugins.IConfigurer)
    implements(IRoutes, inherit=True)
    implements(plugins.ITemplateHelpers)
    implements(plugins.IActions)
    implements(plugins.IUploader)
    implements(interfaces.IDomainObjectModification)
    implements(interfaces.IGroupController)

    def get_resource_uploader(self, data_dict):
        return GobArThemeResourceUploader(data_dict)

    def get_uploader(self, *_):
        '''
        No nos interesa proveer un uploader para el plugin, se usa el default de CKAN.
        '''
        return None

    def get_actions(self):
        return {'package_activity_list_html': gobar_actions.package_activity_list_html,
                'group_delete': gobar_actions.group_delete_and_purge,
                'package_delete': gobar_actions.dataset_delete_and_purge,
                'resource_delete': gobar_actions.resource_delete_and_purge,
                'organization_delete': gobar_actions.organization_delete_and_purge,
                'gobar_status_show': gobar_actions.gobar_status_show}

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_template_directory(config_, '/var/lib/ckan/theme_config/templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('styles/css', 'gobar_css')
        toolkit.add_resource('js', 'gobar_js')
        toolkit.add_resource('recline', 'gobar_data_preview')

    def before_map(self, routing_map):
        gobar_router = gobar_routes.GobArRouter(routing_map)
        gobar_router.set_routes()
        return routing_map

    def get_helpers(self):
        helpers = self.ckan_helpers()
        helpers.update(self.gobar_helpers())
        return helpers

    def ckan_helpers(self):
        return {'get_action': ckan_helpers.get_action}

    def gobar_helpers(self):
        return inspect.getmembers(gobar_helpers, self._is_helper)

    def _is_helper(self, x):
        return callable(x) and getattr(x, '__name__', None) and x.__name__[0] != '_'

    def _prepare_data_for_storage_outside_datajson(self, arguments_list_to_store, entity_dict, object_type):
        '''
        Guardamos en un archivo los datos pertenecientes a ciertas entidades que se pueden perder como consecuencia de
        ciertas operanciones (ej. federar un recurso ya existente implica perder su ícono, en caso de tener uno)
        :param arguments_list_to_store: lista que contiene el nombre de todos los campos que se desean guardar
        :param entity_dict: diccionario correspondiente a la entidad que se está manejando
        :param object_type: string con el tipo de la entidad que se está manejando (ej. groups, resources, etc)
        :return:
        '''
        parameters_to_send = {'id': entity_dict.get('id')}
        for attribute in arguments_list_to_store:
            attribute_value = entity_dict.get(attribute, None)
            if attribute_value is not None:
                parameters_to_send[attribute] = attribute_value
        return self.store_object_data_excluded_from_datajson(object_type, parameters_to_send)

    def store_object_data_excluded_from_datajson(self, object_dict_name, data_dict):
        '''
        :param object_dict_name: string con el tipo de la entidad que se está manejando (ej. groups, resources, etc)
        :param data_dict: diccionario que contiene el id del objeto a guardar y la información que necesitamos almacenar
            pero que no corresponde tener en el data.json (dict); debería poder utilizarse siempre de la misma manera,
            sin importar el tipo del objeto que se desee guardar
        :return: None
        '''
        theme_config = ThemeConfig(constants.CONFIG_PATH)
        data_dict_id = data_dict.get('id', {})
        if data_dict:
            data_dict.pop('id')

            config_item = theme_config.get(object_dict_name, {})
            config_item.update({data_dict_id: data_dict})
            ThemeConfig(constants.CONFIG_PATH).set(object_dict_name, config_item)
            return config_item[data_dict.get('id', data_dict_id)]
        return None

    def notify(self, entity, operation):
        if isinstance(entity, Package):
            if not (operation == 'changed' and entity.state == 'deleted') and entity.state != 'draft':
                datajson_actions.enqueue_update_datajson_cache_tasks()
                cache_actions.clear_web_cache()
        elif isinstance(entity, Resource):
            arguments_list_to_store = ['icon_url']
            entity_dict = entity.as_dict()
            # Modificamos el id dentro de entity_dict para usarlo en el guardado de información en el archivo
            entity_dict['id'] = '%s_%s_%s' % (
                gobar_helpers.get_package_organization(entity_dict.get('package_id')).get('id', ''),
                entity_dict['package_id'],
                entity_dict['id']
            )
            self._prepare_data_for_storage_outside_datajson(arguments_list_to_store, entity_dict, 'resources')

    def create(self, _):
        '''
        Implementación de ckan.plugins.interfaces.IGroupController#create
        Al llamarse esta acción, se regenera la caché del data.json
        '''
        datajson_actions.enqueue_update_datajson_cache_tasks()
        cache_actions.clear_web_cache()

    def edit(self, _):
        '''
        Implementación de ckan.plugins.interfaces.IGroupController#edit
        Al llamarse esta acción, se regenera la caché del data.json
        '''
        datajson_actions.enqueue_update_datajson_cache_tasks()
        cache_actions.clear_web_cache()

    def delete(self, _):
        '''
        Implementación de ckan.plugins.interfaces.IGroupController#delete
        Al llamarse esta acción, se regenera la caché del data.json
        '''
        datajson_actions.enqueue_update_datajson_cache_tasks()
        cache_actions.clear_web_cache()

    def read(self, _):
        '''
        Implementación de ckan.plugins.interfaces.IGroupController#delete
        Al llamarse esta acción, se regenera la caché del data.json
        '''
        pass

    def before_view(self, pkg_dict):
        '''
        Implementación de ckan.plugins.interfaces.IGroupController#before_view
        Vacía intencionalmente, al no necesitar de proveer un hook.
        '''
        return pkg_dict
