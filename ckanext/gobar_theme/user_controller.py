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
import ckan.authz as authz
import smtplib
try:
    from socket import sslerror
except ImportError:
    sslerror = None
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import ckan.lib.authenticator as authenticator
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
                self._set_user_organizations(params['username'], params['organizations[]'])
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

        if 'organizations[]' in params:
            self._set_user_organizations(username, params['organizations[]'])
        self.send_new_user_email(data_dict)
        return {'success': user_created, 'password': random_password}

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
            for user in all_users:
                organizations_and_users[organization.name][user.name] = authz.users_role_for_group_or_org(organization.id, user.id)
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
        email_sender = EmailSender()
        email_sender.send_email(
            msg_body='Te creamos un usuario de andino',
            msg_subject='Usuario de andino creado',
            msg_from='test@test.com',
            msg_to='ignacio.nh@gmail.com'
        )


class EmailSender:
    def __init__(self, smtp_server='localhost', smtp_username=None, smtp_password=None, smtp_use_tls=False):
        self.smtp_server = smtp_server
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_use_tls = smtp_use_tls

    def send_email(self, **kwargs):
        msg = self.assemble_email(kwargs['msg_body'], kwargs['msg_subject'], kwargs['msg_from'], kwargs['msg_to'])
        server = smtplib.SMTP(self.smtp_server)
        if self.smtp_use_tls:
            server.ehlo()
            server.starttls()
            server.ehlo()
        if self.smtp_username and self.smtp_password:
            server.login(self.smtp_username, self.smtp_password)
        server.sendmail(kwargs['msg_from'], kwargs['msg_to'], msg.as_string())
        try:
            server.quit()
        except sslerror:
            # sslerror is raised in tls connections on closing sometimes
            pass

    @staticmethod
    def assemble_email(msg_body, msg_subject, from_address, to_addresses):
        msg = MIMEMultipart()
        msg.set_type('multipart/alternative')
        msg.preamble = msg.epilogue = ''
        text_msg = MIMEText(msg_body)
        text_msg.set_type('text/plain')
        text_msg.set_param('charset', 'ASCII')
        msg.attach(text_msg)
        html_msg = MIMEText(msg_body)
        html_msg.set_type('text/html')
        # @@: Correct character set?
        html_msg.set_param('charset', 'UTF-8')
        html_long = MIMEText(msg_body)
        html_long.set_type('text/html')
        html_long.set_param('charset', 'UTF-8')
        msg.attach(html_msg)
        msg.attach(html_long)
        msg['Subject'] = msg_subject
        msg['From'] = from_address
        msg['To'] = ', '.join(to_addresses)
        return msg
