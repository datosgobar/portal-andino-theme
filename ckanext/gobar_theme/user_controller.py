import ckan.lib.base as base
from ckan.common import request, c, _
import ckan.logic as logic
import ckan.model as model
from ckan.controllers.user import UserController
import ckan.lib.helpers as h
import ckan.plugins as p
from webob.exc import HTTPNotFound

parse_params = logic.parse_params
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized


class GobArUserController(UserController):

    def read(self, id=None):
        if id and id == c.user:
            return super(GobArUserController, self).read(id)
        if id == 'logged_in':
            try:
                return super(GobArUserController, self).read(id)
            except HTTPNotFound:
                return h.redirect_to(controller='ckanext.gobar_theme.user_controller:GobArUserController', action='login', login_error=True)
        return h.redirect_to('home')

    def login(self, error=None):
        # Do any plugin login stuff
        for item in p.PluginImplementations(p.IAuthenticator):
            item.login()

        if not c.user:
            came_from = request.params.get('came_from')
            if not came_from:
                came_from = h.url_for(controller='user', action='logged_in',
                                      __ckan_no_root=True)
            c.login_handler = h.url_for(
                self._get_repoze_handler('login_handler_path'),
                came_from=came_from)
            vars = {'login_error': parse_params(request.GET).get('login_error')}
            return base.render('user/login.html', extra_vars=vars)
        else:
            return h.redirect_to('home')

    def my_account(self):
        self._authorize()
        return base.render('user/user_config_my_account.html')

    def my_account_edit_email(self):
        self._authorize()
        if request.method == 'POST':
            post_params = parse_params(request.POST)
            email = post_params['email']
            user_data = {
                'id': c.userobj.id,
                'email': email
            }
            user_updated = self._edit_user(user_data)
            return h.json.dumps({'success': user_updated}, for_json=True)
        else:
            return h.redirect_to('/configurar/mi_cuenta')

    def my_account_edit_password(self):
        self._authorize()
        if request.method == 'POST':
            post_params = parse_params(request.POST)
            password = post_params['password']
            user_data = {
                'id': c.userobj.id,
                'password': password
            }
            user_updated = self._edit_user(user_data)
            return h.json.dumps({'success': user_updated}, for_json=True)
        else:
            return h.redirect_to('/configurar/mi_cuenta')

    def create_users(self):
        # todo: modificar
        # path_to_virtualenv/src/ckan/ckan/lib/cli.py
        # class UserCmd
        self._authorize(sysadmin_required=True)
        extra_vars = {}
        if request.method == 'POST':
            params = parse_params(request.POST)
            data_dict = {
                'name': params['name'],
                'email': params['email'],
                'password': params['password'],
                'sysadmin': 'admin' in params
            }
            extra_vars['user'] = data_dict
            site_user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
            context = {
                'model': model,
                'session': model.Session,
                'ignore_auth': True,
                'user': site_user['name'],
            }
            try:
                logic.get_action('user_create')(context, data_dict)
                user_created = True
            except logic.ValidationError, e:
                user_created = False
                extra_vars['errors'] = e.error_dict
            extra_vars['user_created'] = user_created
        return base.render('user/user_config_create_users.html', extra_vars=extra_vars)

    def user_history(self):
        # todo
        return ''

    def list_users(self):
        # todo: sacar
        self._authorize()
        extra_vars = {'users': model.Session.query(model.User)}
        return base.render('user/user_config_list_users.html', extra_vars=extra_vars)

    @staticmethod
    def _edit_user(data_dict):
        site_user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'ignore_auth': True, 'user': site_user['name']}
        try:
            logic.get_action('user_update')(context, data_dict)
            user_updated = True
        except logic.ValidationError, e:
            user_updated = False
        return user_updated

    @staticmethod
    def _authorize(sysadmin_required=False):
        if sysadmin_required:
            context = {'model': model, 'user': c.user, 'auth_user_obj': c.userobj}
            try:
                logic.check_access('sysadmin', context, {})
                return True
            except logic.NotAuthorized:
                return h.redirect_to('home')
        else:
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj,
                       'save': 'save' in request.params}
            try:
                check_access('package_create', context)
                return True
            except NotAuthorized:
                base.abort(401, _('Unauthorized to change config'))
