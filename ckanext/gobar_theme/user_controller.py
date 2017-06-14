import ckan.lib.base as base
from ckan.common import request, c, _, response
import ckan.logic as logic
import ckan.model as model
from ckan.controllers.user import UserController
import ckan.lib.helpers as h
import ckan.plugins as p
from webob.exc import HTTPNotFound
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.activity_streams as activity_streams

parse_params = logic.parse_params
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized


class GobArUserController(UserController):
    json_content_type = 'application/json;charset=utf-8'

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
            response.headers['Content-Type'] = self.json_content_type
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
            response.headers['Content-Type'] = self.json_content_type
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
        all_users = model.Session.query(model.User).filter_by(state='active')
        extra_vars['admin_users'] = list(filter(lambda u: u.sysadmin, all_users))
        extra_vars['normal_users'] = list(filter(lambda u: not u.sysadmin, all_users))
        return base.render('user/user_config_create_users.html', extra_vars=extra_vars)

    def user_history(self):
        self._authorize()
        if c.userobj.sysadmin:
            users = model.Session.query(model.User)
            activity_queries = []
            for user in users:
                activity_queries += self._get_activity(user)
        else:
            activity_queries = self._get_activity(c.userobj)

        sql_activities = model.activity._activities_union_all(*activity_queries)

        offset, limit = 0, 100
        raw_activities = model.activity._activities_at_offset(sql_activities, limit, offset)
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author, 'auth_user_obj': c.userobj, 'for_view': True}
        activities = model_dictize.activity_list_dictize(raw_activities, context)
        extra_vars = {
            'controller': 'user',
            'action': 'activity',
            'offset': offset,
            'user_history': True
        }
        activities = activity_streams.activity_list_to_html(context, activities, extra_vars)
        return base.render('user/user_config_history.html', extra_vars={'activities': activities})

    def delete_user(self):
        user_deleted = False
        if request.method == 'POST':
            params = parse_params(request.POST)
            try:
                user = model.User.by_name(params['id'])
                user.delete()
                model.repo.commit_and_remove()
                user_deleted = True
            except NotAuthorized:
                user_deleted = False
        response.headers['Content-Type'] = self.json_content_type
        return h.json.dumps({'success': user_deleted}, for_json=True)

    @staticmethod
    def _edit_user(data_dict):
        if 'email' not in data_dict:
            data_dict['email'] = model.User.get(data_dict['id']).email
        site_user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'ignore_auth': True, 'user': site_user['name']}
        try:
            logic.get_action('user_update')(context, data_dict)
            user_updated = True
        except logic.ValidationError, e:
            user_updated = False
        return user_updated

    @staticmethod
    def _get_activity(user):
        user = model.User.get(user.id)
        return [
            model.activity._activities_from_user_query(user.id),
            model.activity._activities_about_user_query(user.id)
        ]

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
