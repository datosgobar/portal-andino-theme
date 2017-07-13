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
import random
import string
import ckanext.gobar_theme.mailer as mailer
import ckan.lib.mailer as ckan_mailer
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
                controller = 'ckanext.gobar_theme.user_controller:GobArUserController'
                return h.redirect_to(controller=controller, action='login', login_error=True)
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
            extra_vars = {'login_error': parse_params(request.GET).get('login_error')}
            return base.render('user/login.html', extra_vars=extra_vars)
        else:
            return h.redirect_to('home')

    def password_forgot(self):
        json_response = {'success': False}
        access_context = {'model': model, 'session': model.Session, 'user': c.user, 'auth_user_obj': c.userobj}
        try:
            check_access('request_reset', access_context)
        except NotAuthorized:
            base.abort(401, _('Unauthorized to request reset password.'))

        if request.method == 'POST':
            user_id = parse_params(request.POST).get('user')
            context = {'model': model, 'user': c.user}
            data_dict = {'id': user_id}
            user_obj = None
            try:
                logic.get_action('user_show')(context, data_dict)
                user_obj = context['user_obj']
            except logic.NotFound:
                # Try searching the user
                del data_dict['id']
                data_dict['q'] = user_id

                if user_id and len(user_id) > 2:
                    user_list = logic.get_action('user_list')(context, data_dict)
                    if len(user_list) == 1:
                        # This is ugly, but we need the user object for the mailer, and user_list does not return them
                        del data_dict['q']
                        data_dict['id'] = user_list[0]['id']
                        logic.get_action('user_show')(context, data_dict)
                        user_obj = context['user_obj']
                    elif len(user_list) > 1:
                        json_response['error'] = 'several_users'
                    else:
                        json_response['error'] = 'not_found'
                else:
                    json_response['error'] = 'not_found'

            if user_obj:
                try:
                    mail_sent = mailer.send_reset_link(user_obj)
                    json_response['success'] = mail_sent
                except mailer.MailerException, e:
                    json_response['error'] = 'unkown'
                    print(e)
        response.headers['Content-Type'] = self.json_content_type
        return h.json.dumps(json_response, for_json=True)

    def password_reset(self, user_id):
        context = {'model': model, 'session': model.Session, 'user': user_id, 'keep_email': True}
        try:
            check_access('user_reset', context)
        except NotAuthorized:
            return h.redirect_to('home')

        try:
            logic.get_action('user_show')(context, {'id': user_id})
            user_obj = context['user_obj']
        except logic.NotFound:
            return base.abort(404)

        c.reset_key = request.params.get('key')
        if not ckan_mailer.verify_reset_link(user_obj, c.reset_key):
            # Invalid reset key.
            return base.abort(404)

        if request.method == 'POST':
            user_data = {
                'id': user_obj.id,
                'password': request.params.get('password')
            }
            if request.params.get('email', None) is not None:
                user_data['email'] = request.params.get('email')
            user_updated = self._edit_user(user_data)
            ckan_mailer.create_reset_key(user_obj)
            response.headers['Content-Type'] = self.json_content_type
            json_response = {
                'success': user_updated,
                'redirect_url': h.url_for('/ingresar')
            }
            return h.json.dumps(json_response, for_json=True)
        return base.render('user/perform_reset.html', extra_vars={'user': user_obj})

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
            current_password = post_params['current-password']
            current_password_is_valid = self.validate_password(current_password)
            password = post_params['password']
            user_data = {
                'id': c.userobj.id,
                'password': password
            }
            user_updated = current_password_is_valid and self._edit_user(user_data)
            json_response = {'success': user_updated}
            if not current_password_is_valid:
                json_response['error'] = 'current_password'
            response.headers['Content-Type'] = self.json_content_type
            return h.json.dumps(json_response, for_json=True)
        else:
            return h.redirect_to('/configurar/mi_cuenta')

    def create_users(self):
        self._authorize(sysadmin_required=True)
        extra_vars = {}
        if request.method == 'POST':
            json_response = self._create_user()
            response.headers['Content-Type'] = self.json_content_type
            return h.json.dumps(json_response, for_json=True)
        all_users = model.Session.query(model.User).filter_by(state='active')
        extra_vars['admin_users'] = list(filter(lambda u: u.sysadmin, all_users))
        extra_vars['normal_users'] = list(filter(lambda u: not u.sysadmin, all_users))
        extra_vars['organizations_and_users'] = self._roles_by_organization()
        return base.render('user/user_config_create_users.html', extra_vars=extra_vars)

    def user_history(self):
        self._authorize()
        params = parse_params(request.GET)
        if params.get('page'):
            page = int(params['page'])
        else:
            page = 1
        activities, has_more = self._activities(page)
        if params.get('raw'):
            response.headers['X-has-more'] = has_more
            return activities
        else:
            extra_vars = {'activities': activities, 'has_more': has_more}
            return base.render('user/user_config_history.html', extra_vars=extra_vars)

    def edit_user(self):
        self._authorize(sysadmin_required=True)
        user_edited = False
        if request.method == 'POST':
            params = parse_params(request.POST)
            user_data = {
                'id': params['username'],
                'sysadmin': params['role'] == 'admin'
            }
            if params['role'] != 'admin':
                self._set_user_organizations(params['username'], params.get('organizations[]', []))
            user_edited = self._edit_user(user_data)
        response.headers['Content-Type'] = self.json_content_type
        return h.json.dumps({'success': user_edited}, for_json=True)

    def delete_user(self):
        self._authorize(sysadmin_required=True)
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
        except logic.ValidationError:
            user_updated = False
        return user_updated

    @staticmethod
    def _get_activity(user):
        user = model.User.get(user.id)
        return [
            model.activity._activities_from_user_query(user.id),
            model.activity._activities_about_user_query(user.id)
        ]

    def _create_user(self):
        params = parse_params(request.POST)
        username = params['username']
        if model.User.by_name(username) is not None:
            return {'success': False, 'error': 'user_already_exists'}
        random_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        data_dict = {
            'name': username,
            'fullname': params['fullname'],
            'email': params['email'],
            'password': random_password,
            'sysadmin': 'admin' in params
        }
        site_user = logic.get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        context = {'model': model, 'session': model.Session, 'ignore_auth': True, 'user': site_user['name']}
        try:
            logic.get_action('user_create')(context, data_dict)
            user_created = True
        except logic.ValidationError, e:
            user_created = False
            print(e.error_dict)
            print(e.error_summary)

        email_sent = False
        if user_created:
            if 'organizations[]' in params:
                self._set_user_organizations(username, params['organizations[]'])
            email_sent = self.send_new_user_email(data_dict)
        return {'success': user_created, 'password': random_password, 'email_sent': email_sent}

    @staticmethod
    def _set_user_organizations(username, user_organizations):
        for organization in model.Session.query(model.Group).filter_by(state='active'):
            data_dict = {
                'id': organization.id,
                'username': username,
                'role': 'editor'
            }
            context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
            if organization.name in user_organizations:
                logic.get_action('group_member_create')(context, data_dict)
            else:
                logic.get_action('group_member_delete')(context, data_dict)

    @staticmethod
    def _roles_by_organization():
        all_users = model.Session.query(model.User).filter_by(state='active')
        organizations_and_users = {}
        for organization in model.Session.query(model.Group).filter_by(state='active'):
            organizations_and_users[organization.name] = {}
            users_in_organization = filter(
                lambda m: m.table_name == 'user' and m.state == 'active' and m.capacity == 'editor',
                organization.member_all
            )
            users_id_in_organization = map(lambda u: u.table_id, users_in_organization)
            for user in all_users:
                if user.id in users_id_in_organization:
                    organizations_and_users[organization.name][user.name] = True
                else:
                    organizations_and_users[organization.name][user.name] = None
        return organizations_and_users

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

    @staticmethod
    def validate_password(password):
        user = model.User.by_name(c.user)
        return user.validate_password(password)

    @staticmethod
    def send_new_user_email(data_dict):
        admin_user = c.userobj
        new_user = model.User.get(data_dict['name'])
        postfix_response = mailer.send_new_user_mail(admin_user, new_user)
        print(postfix_response)
        return postfix_response['success']

    def _activities(self, page):
        limit = 100
        offset = (page-1) * limit
        if c.userobj.sysadmin:
            users = model.Session.query(model.User)
            activity_queries = []
            for user in users:
                activity_queries += self._get_activity(user)
        else:
            activity_queries = self._get_activity(c.userobj)

        sql_activities = model.activity._activities_union_all(*activity_queries)
        total_count = sql_activities.count()
        has_more = total_count > offset+limit
        raw_activities = model.activity._activities_at_offset(sql_activities, limit, offset)
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        activities = model_dictize.activity_list_dictize(raw_activities, context)
        extra_vars = {
            'controller': 'user',
            'action': 'activity',
            'offset': offset,
            'user_history': True
        }
        return activity_streams.activity_list_to_html(context, activities, extra_vars), has_more
