# coding=utf-8
from routes.mapper import SubMapper
from pylons.config import config


class GobArRouter:

    def __init__(self, route_map):
        self.route_map = route_map

        self.home_controller = 'ckanext.gobar_theme.controller:GobArHomeController'
        self.home_routes = SubMapper(self.route_map, controller=self.home_controller)
        self.api_controller = 'ckanext.gobar_theme.controller:GobArApiController'
        self.package_controller = 'ckanext.gobar_theme.package_controller:GobArPackageController'
        self.config_controller = 'ckanext.gobar_theme.config_controller:GobArConfigController'
        self.user_controller = 'ckanext.gobar_theme.user_controller:GobArUserController'
        self.google_analytics_controller = 'ckanext.gobar_theme.google_analytics_controller:GobArGAController'
        self.spatial_controller = 'ckanext.gobar_theme.spatial_controller:GobArSpatialController'
        self.datajson_controller = 'ckanext.gobar_theme.datajson_controller:GobArDatajsonController'

    def redirect(self, *routes):
        for url_from, url_to in routes:
            self.route_map.redirect(url_from, url_to)

    def set_routes(self):
        self.connect_home()
        self.connect_static()
        self.connect_section()
        self.connect_datasets()
        self.connect_organizations()
        self.connect_groups()
        self.connect_apis()
        self.connect_users()
        self.remove_dashboard()
        self.remove_tags()
        self.remove_revision()
        # self.remove_admin()
        self.connect_api()
        self.connect_template_config()
        self.connect_google_analytics()
        self.connect_spatial()
        self.connect_datajson()
        self.connect_super_theme_taxonomy()

    def connect_home(self):
        self.home_routes.connect('/', action='index')

    def connect_super_theme_taxonomy(self):
        self.home_routes.connect('/superThemeTaxonomy.json', action='super_theme_taxonomy')

    def connect_static(self):
        self.home_routes.connect('gobar_about', '/acerca', action='about')
        self.home_routes.connect('gobar_about_ckan', '/acerca/ckan', action='about_ckan')
        self.redirect(
            ('/about', '/acerca')
        )

    def connect_section(self):
        self.home_routes.connect('section', '/acerca/seccion/{title}', action='view_about_section')

    def connect_google_analytics(self):
        with SubMapper(self.route_map, controller=self.google_analytics_controller) as m:
            m.connect('resource view embed', '/dataset/resource_view_embed/{resource_id}', action='resource_view_embed')


    def connect_spatial(self):
        with SubMapper(self.route_map, controller=self.spatial_controller) as m:
            m.connect('countries', '/spatial/paises', action='paises'),
            m.connect('provinces', '/spatial/provincias', action='provincias'),
            m.connect('districts', '/spatial/localidades', action='localidades'),
            m.connect('districts', '/spatial/localidades/{province_id}', action='localidades'),
            m.connect('districts', '/spatial/municipios', action='municipios'),
            m.connect('districts', '/spatial/municipios/{province_id}', action='municipios'),

    def connect_apis(self):
        self.home_routes.connect('gobar_apis', '/apis', action='apis')
        self.redirect(
            ('/apis', '/apis'),
        )

    def connect_datasets(self):
        with SubMapper(self.route_map, controller=self.package_controller) as m:
            m.connect('search', '/dataset', action='search', highlight_actions='index search')
            m.connect('add dataset', '/dataset/new', action='new')
            m.connect('edit dataset', '/dataset/edit/{id}', action='edit')
            m.connect('delete dataset', '/dataset/delete/{id}', action='delete')
            m.connect('new resource', '/dataset/new_resource/{id}', action='new_resource')
            m.connect('edit resource', '/dataset/{id}/resource_edit/{resource_id}', action='resource_edit')
            m.connect('delete resource', '/dataset/{id}/resource_delete/{resource_id}', action='resource_delete')
        self.route_map.connect('/dataset/{id}/archivo/{resource_id}', action='resource_read', controller='package')
        self.redirect(
            ('/dataset/history/{id:.*?}', '/dataset/{id}'),
            ('/dataset/activity/{id:.*?}', '/dataset/{id}'),
            ('/dataset/groups/{id:.*?}', '/dataset/{id}'),
            ('/dataset/followers/{id:.*?}', '/dataset/{id}'),
            ('/dataset/{id}/resource/{resource_id}', '/dataset/{id}/archivo/{resource_id}')
        )

    def remove_dashboard(self):
        self.redirect(
            ('/dashboard', '/'),
            ('/dashboard/datasets', '/'),
            ('/dashboard/groups', '/'),
            ('/dashboard/organizations', '/'),
            ('/dashboard/{url:.*?}', '/dashboard')
        )

    def connect_organizations(self):
        self.route_map.connect('/organizaciones', action='index', controller='organization')
        self.route_map.connect('/organization/new', action='new', controller='organization')
        self.redirect(
            ('/organization', '/organizaciones'),
            ('/organization/list', '/organization'),
            ('/organization/{id}', '/organization/list'),
            ('/organization/activity/{id}/{offset}', '/organization/list'),
            ('/organization/about/{id}', '/organization/list'),
            ('/organization/admins/{id}', '/organization/list'),
            ('/organization/members/{id}', '/organization/list'),
            ('/organization/member_new/{id}', '/organization/list'),
            ('/organization/member_delete/{id}', '/organization/list'),
            ('/organization/history/{id}', '/organization/list'),
            ('/organization/bulk_process/{id}', '/organization/list')
        )

    def connect_groups(self):
        self.route_map.connect('group_new', '/group/new', action='new', controller='group')
        self.redirect(
            ('/group', '/'),
            ('/group/list', '/'),
            ('/group/{id}', '/group/list'),
            ('/group/about/{id}', '/group/list'),
            ('/group/members/{id}', '/group/list'),
            ('/group/member_new/{id}', '/group/list'),
            ('/group/member_delete/{id}', '/group/list'),
            ('/group/history/{id}', '/group/list'),
            ('/group/followers/{id}', '/group/list'),
            ('/group/follow/{id}', '/group/list'),
            ('/group/unfollow/{id}', '/group/list'),
            ('/group/admins/{id}', '/group/list'),
            ('/group/activity/{id}/{offset}', '/group/list')
        )

    def connect_users(self):
        self.route_map.connect('/logout', action='logout', controller='user')
        with SubMapper(self.route_map, controller=self.user_controller) as m:
            m.connect('/borradores', action="drafts")
            m.connect('/user/reset/{user_id}', action="password_reset")
            m.connect('user_datasets', '/user/{id:.*}', action='read')
            m.connect('login', '/ingresar', action='login')
            m.connect('/olvide_mi_contraseña', action="password_forgot")
            m.connect('/configurar/mi_cuenta', action="my_account")
            m.connect('/configurar/mi_cuenta/cambiar_email', action="my_account_edit_email")
            m.connect('/configurar/mi_cuenta/cambiar_contraseña', action="my_account_edit_password")
            m.connect('/configurar/crear_usuarios', action="create_users")
            m.connect('/configurar/editar_usuario', action="edit_user")
            m.connect('/configurar/borrar_usuario', action="delete_user")
            m.connect('/configurar/historial', action="user_history")
            m.connect('/configurar/historial.json', action="user_history_json")

        self.redirect(
            ('/user/login', '/'),
            ('/user/generate_key/{id}', '/'),
            ('/user/activity/{id}/{offset}', '/'),
            ('/user/activity/{id}', '/'),
            ('/user/follow/{id}', '/'),
            ('/user/unfollow/{id}', '/'),
            ('/user/followers/{id:.*}', '/'),
            ('/user/delete/{id}', '/'),
            ('/user/register', '/'),
            ('/user/reset', '/'),
            ('/user/set_lang/{lang}', '/'),
            ('/user', '/'),
            ('/user/_logout', '/logout'),
            ('/user/logged_out_redirect', '/'),
            ('/salir', '/logout')
        )

    def remove_tags(self):
        self.redirect(
            ('/tag', '/'),
            ('/tag/{url}', '/')
        )

    def remove_revision(self):
        self.redirect(
            ('/revision', '/'),
            ('/revision/list', '/'),
            ('/revision/edit/{id}', '/revision'),
            ('/revision/diff/{id}', '/revision'),
            ('/revision/{id}', '/revision')
        )

    def remove_admin(self):
        self.redirect(
            ('/ckan-admin', '/'),
            ('/ckan-admin/config', '/'),
            ('/ckan-admin/trash', '/'),
            ('/ckan-admin/{action}', '/')
        )

    def connect_api(self):
        with SubMapper(self.route_map, controller=self.api_controller, path_prefix='/api{ver:/3|}', ver='/3') as m:
            m.connect('/action/{logic_function}', action='action', conditions=dict(method=['GET', 'POST']))
            m.connect('/util/status', action='status')

    def connect_template_config(self):
        with SubMapper(self.route_map, controller=self.config_controller) as m:
            m.connect('/configurar/titulo', action='edit_title')
            m.connect('/configurar/portada', action='edit_home')
            m.connect('/configurar/encabezado', action='edit_header')
            m.connect('/configurar/temas', action='edit_groups')
            m.connect('/configurar/redes', action='edit_social')
            m.connect('/configurar/pie-de-pagina', action='edit_footer')
            m.connect('/configurar/datasets', action='edit_datasets')
            m.connect('/configurar/organizaciones', action='edit_organizations')
            m.connect('/configurar/acerca', action='edit_about')
            m.connect('/configurar/apis', action='edit_apis')
            m.connect('/configurar/metadata/google_fb', action='edit_metadata_google_fb')
            m.connect('/configurar/metadata/tw', action='edit_metadata_tw')
            m.connect('/configurar/metadata/portal', action='edit_metadata_portal')
            m.connect('/configurar/mensaje_de_bienvenida', action='edit_greetings')

        self.redirect(
            ('/configurar', '/configurar/titulo'),
            ('/configurar', '/configurar/metadata')
        )

    def connect_datajson(self):
        with SubMapper(self.route_map, controller=self.datajson_controller) as m:
            m.connect('datajson', '/data.json', action='datajson')
        self.redirect(
            ('/datajson', '/datajson'),
        )

        disable_catalog_xlsx_url = config.get('andino.disable_catalog_xlsx_url')
        if disable_catalog_xlsx_url in ('True', 'true', '1', 'Yes', 'yes', ):
            self.redirect(
                ('/catalog.xlsx', '/'),  # Redirecciono a la home
            )
