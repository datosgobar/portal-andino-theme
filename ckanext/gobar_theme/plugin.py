#! coding: utf-8
from uploader import GobArThemeResourceUploader
import ckan.plugins as plugins
from ckan.model.package import Package
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as ckan_helpers
import ckan.plugins.interfaces as interfaces
from ckan.plugins import implements, IRoutes
import ckanext.gobar_theme.helpers as gobar_helpers
import ckanext.gobar_theme.routing as gobar_routes
import ckanext.gobar_theme.actions as gobar_actions
import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
from ckanext.gobar_theme.lib import cache_actions


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
            'get_suborganizations': gobar_helpers.get_suborganizations,
            'get_faceted_groups': gobar_helpers.get_faceted_groups,
            'join_groups': gobar_helpers.join_groups,
            'cut_text': gobar_helpers.cut_text,
            'cut_img_path': gobar_helpers.cut_img_path,
            'organizations_with_packages': gobar_helpers.organizations_with_packages,
            'get_pkg_extra': gobar_helpers.get_pkg_extra,
            'get_facet_items_dict': gobar_helpers.get_facet_items_dict,
            'get_theme_config': gobar_helpers.get_theme_config,
            'url_join': gobar_helpers.url_join,
            'json_loads': gobar_helpers.json_loads,
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
        }

    def notify(self, entity, operation):
        if type(entity) is Package:
            if not (operation == 'changed' and entity.state == 'deleted') and entity.state != 'draft':
                datajson_actions.enqueue_update_datajson_cache_tasks()
                cache_actions.clear_web_cache()


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
