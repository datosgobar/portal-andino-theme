import ckan.lib.base as base
from ckan.common import request, c, _
import ckan.logic as logic
import ckan.model as model

parse_params = logic.parse_params
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized


class GobArUserController(base.BaseController):

    def my_account(self):
        return ''

    def create_users(self):
        # path_to_virtualenv/src/ckan/ckan/lib/cli.py
        # class UserCmd
        self._authorize()
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

    def list_users(self):
        self._authorize()
        extra_vars = {'users': model.Session.query(model.User)}
        return base.render('user/user_config_list_users.html', extra_vars=extra_vars)

    def edit_user(self):
        self._authorize()
        get_params = parse_params(request.GET)
        username = get_params['username']
        user = model.User.get(username)
        extra_vars = {'user': user}
        if request.method == 'POST':
            post_params = parse_params(request.POST)
            data_dict = {
                'id': user.id,
                'name': post_params['name'],
                'email': post_params['email'],
                'password': post_params['password'],
                'sysadmin': 'admin' in post_params
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
                logic.get_action('user_update')(context, data_dict)
                user_updated = True
            except logic.ValidationError, e:
                user_updated = False
                extra_vars['errors'] = e.error_dict
            extra_vars['user_updated'] = user_updated
        return base.render('user/user_config_edit_user.html', extra_vars=extra_vars)

    @staticmethod
    def _authorize():
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'save': 'save' in request.params}
        try:
            check_access('package_create', context)
            return True
        except NotAuthorized:
            base.abort(401, _('Unauthorized to change config'))
