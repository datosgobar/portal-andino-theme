#! coding: utf-8
# pylint: disable-all
import ckan.lib.helpers as ckan_helpers
import ckan.plugins as plugins
import ckan.plugins.interfaces as interfaces
import ckan.plugins.toolkit as toolkit
from ckan.model.package import Package
from ckan.model.resource import Resource
from ckan.plugins import implements, IRoutes

import ckanext.gobar_theme.actions as gobar_actions
import ckanext.gobar_theme.helpers as gobar_helpers
import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
import ckanext.gobar_theme.routing as gobar_routes
from ckanext.gobar_theme.lib import cache_actions
from uploader import GobArThemeResourceUploader
from .utils.ckan_utils import is_plugin_present


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
        return {
            'organization_tree': gobar_helpers.organization_tree,
            'get_suborganizations_names': gobar_helpers.get_suborganizations_names,
            'get_faceted_groups': gobar_helpers.get_faceted_groups,
            'join_groups': gobar_helpers.join_groups,
            'cut_text': gobar_helpers.cut_text,
            'cut_img_path': gobar_helpers.cut_img_path,
            'organizations_with_packages': gobar_helpers.organizations_with_packages,
            'get_pkg_extra': gobar_helpers.get_pkg_extra,
            'get_theme_config': gobar_helpers.get_theme_config,
            'url_join': gobar_helpers.url_join,
            'json_loads': gobar_helpers.json_loads,
            'license_options': gobar_helpers.license_options,
            'get_license_title': gobar_helpers.get_license_title,
            'id_belongs_to_license': gobar_helpers.id_belongs_to_license,
            'update_frequencies': gobar_helpers.update_frequencies,
            'field_types': gobar_helpers.field_types,
            'distribution_types': gobar_helpers.distribution_types,
            'special_field_types': gobar_helpers.special_field_types,
            'render_ar_datetime': gobar_helpers.render_ar_datetime,
            'accepted_mime_types': gobar_helpers.accepted_mime_types,
            'package_resources': gobar_helpers.package_resources,
            'valid_length': gobar_helpers.valid_length,
            'capfirst': gobar_helpers.capfirst,
            'type_is_numeric': gobar_helpers.type_is_numeric,
            'attributes_has_at_least_one': gobar_helpers.attributes_has_at_least_one,
            'portal_andino_version': gobar_helpers.portal_andino_version,
            'get_distribution_metadata': gobar_helpers.get_distribution_metadata,
            'is_distribution_local': gobar_helpers.is_distribution_local,
            'get_extra_value': gobar_helpers.get_extra_value,
            'remove_url_param': gobar_helpers.remove_url_param,
            'get_action': ckan_helpers.get_action,
            'get_groups_img_paths': gobar_helpers.get_groups_img_paths,
            'fetch_groups': gobar_helpers.fetch_groups,
            'date_format_to_iso': gobar_helpers.date_format_to_iso,
            'jsondump': gobar_helpers.jsondump,
            'get_default_background_configuration': gobar_helpers.get_default_background_configuration,
            'get_gtm_code': gobar_helpers.get_gtm_code,
            'get_current_url_for_resource': gobar_helpers.get_current_url_for_resource,
            'get_package_organization': gobar_helpers.get_package_organization,
            'store_object_data_excluded_from_datajson': gobar_helpers.store_object_data_excluded_from_datajson,
            'get_resource_icon': gobar_helpers.get_resource_icon,
            'get_andino_base_page': gobar_helpers.get_andino_base_page,
            'is_plugin_present': is_plugin_present,
            'organizations_basic_info': gobar_helpers.organizations_basic_info,
            'get_default_series_api_url': gobar_helpers.get_default_series_api_url,
            'create_or_update_cron_job': gobar_helpers.create_or_update_cron_job,
            'get_current_terminal_username': gobar_helpers.get_current_terminal_username,
            'get_organizations_tree': gobar_helpers.get_organizations_tree,
            'prepare_context_variable': gobar_helpers.prepare_context_variable,
        }

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
        return gobar_helpers.store_object_data_excluded_from_datajson(object_type, parameters_to_send)

    def notify(self, entity, operation):
        if type(entity) is Package:
            if not (operation == 'changed' and entity.state == 'deleted') and entity.state != 'draft':
                datajson_actions.enqueue_update_datajson_cache_tasks()
                cache_actions.clear_web_cache()
        elif type(entity) is Resource:
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
