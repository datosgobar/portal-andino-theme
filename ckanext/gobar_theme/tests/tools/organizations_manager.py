# encoding: utf-8
import json
import functools
import ckan.common
import ckan.plugins as p
import ckan.logic as logic
import ckan.authz as authz
import ckan.plugins as plugins
import ckan.lib.munge as munge
import ckan.lib.dictization as d
import ckan.lib.search as search
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories
from ckan import model
from collections import defaultdict
from paste.deploy.converters import asbool
from ckan.logic import _actions, _is_chained_action, _prepopulate_context


def create_organization(name, parent=''):
    data_dict = {'name': name}
    if parent:
        data_dict['groups'] = [{'name': parent}]
    context = {'user': factories._get_action_user_name(data_dict)}
    data_dict.setdefault('type', 'organization')
    return helpers.call_action('organization_create', context=context, **data_dict)


# Mock functions


def get_action(action):
    if _actions:
        if action not in _actions:
            if action == 'package_search':
                return package_search
            raise KeyError("Action '%s' not found" % action)
        return _actions.get(action)
    for action_module_name in ['get', 'create', 'update', 'delete', 'patch']:
        module_path = 'ckan.logic.action.' + action_module_name
        module = __import__(module_path)
        for part in module_path.split('.')[1:]:
            module = getattr(module, part)
        for k, v in module.__dict__.items():
            if not k.startswith('_'):
                if (hasattr(v, '__call__') and
                        (v.__module__ == module_path or
                         hasattr(v, '__replaced'))):
                    _actions[k] = v
                    if action_module_name == 'get' and \
                       not hasattr(v, 'side_effect_free'):
                        v.side_effect_free = True
    resolved_action_plugins = {}
    fetched_actions = {}
    chained_actions = defaultdict(list)
    for plugin in p.PluginImplementations(p.IActions):
        for name, auth_function in plugin.get_actions().items():
            if _is_chained_action(auth_function):
                chained_actions[name].append(auth_function)
            elif name in resolved_action_plugins:
                raise Exception('The action %r is already implemented in %r' % (name, resolved_action_plugins[name]))
            else:
                resolved_action_plugins[name] = plugin.name
                auth_function.auth_audit_exempt = True
                fetched_actions[name] = auth_function
    for name, func_list in chained_actions.iteritems():
        if name not in fetched_actions:
            raise Exception('The action %r is not found for chained action' % (
                name))
        for func in reversed(func_list):
            prev_func = fetched_actions[name]
            fetched_actions[name] = functools.partial(func, prev_func)
    _actions.update(fetched_actions)
    for action_name, _action in _actions.items():
        def make_wrapped(_action, action_name):
            def wrapped(context=None, data_dict=None, **kw):
                if kw:
                    pass
                context = _prepopulate_context(context)
                context.setdefault('__auth_audit', [])
                context['__auth_audit'].append((action_name, id(_action)))
                result = _action(context, data_dict, **kw)
                try:
                    audit = context['__auth_audit'][-1]
                    if audit[0] == action_name and audit[1] == id(_action):
                        if action_name not in authz.auth_functions_list():
                            pass
                        elif not getattr(_action, 'auth_audit_exempt', False):
                            raise Exception('Action function {0} did not call its auth function'.format(action_name))
                        context['__auth_audit'].pop()
                except IndexError:
                    pass
                return result
            return wrapped
        if hasattr(_action, '__replaced'):
            _actions[action_name] = _action.__replaced
            continue

        fn = make_wrapped(_action, action_name)
        fn.__doc__ = _action.__doc__
        if getattr(_action, 'side_effect_free', False):
            fn.side_effect_free = True
        _actions[action_name] = fn

    return _actions.get(action)


def package_search(context, data_dict):
    schema = (context.get('schema') or logic.schema.default_package_search_schema())
    data_dict.update(data_dict.get('__extras', {}))
    data_dict.pop('__extras', None)
    session = model.Session
    # session = context['session']
    user = context.get('user')
    data_dict['extras'] = data_dict.get('extras', {})
    for key in [key for key in data_dict.keys() if key.startswith('ext_')]:
        data_dict['extras'][key] = data_dict.pop(key)
    abort = data_dict.get('abort_search', False)
    if data_dict.get('sort') in (None, 'rank'):
        data_dict['sort'] = 'score desc, metadata_modified desc'
    results = []
    if not abort:
        if asbool(data_dict.get('use_default_schema')):
            data_source = 'data_dict'
        else:
            data_source = 'validated_data_dict'
        data_dict.pop('use_default_schema', None)

        result_fl = data_dict.get('fl')
        if not result_fl:
            data_dict['fl'] = 'id {0}'.format(data_source)
        else:
            data_dict['fl'] = ' '.join(result_fl)
        include_private = asbool(data_dict.pop('include_private', False))
        include_drafts = asbool(data_dict.pop('include_drafts', False))
        data_dict.setdefault('fq', '')
        if not include_private:
            data_dict['fq'] = '+capacity:public ' + data_dict['fq']
        if include_drafts:
            data_dict['fq'] += ' +state:(active OR draft)'
        extras = data_dict.pop('extras', None)
        query = search.query_for(model.Package)
        query.run(data_dict, permission_labels=None)
        data_dict['extras'] = extras
        if result_fl:
            for package in query.results:
                if package.get('extras'):
                    package.update(package['extras'] )
                    package.pop('extras')
                results.append(package)
        else:
            for package in query.results:
                package_dict = package.get(data_source)
                if package_dict:
                    package_dict = json.loads(package_dict)
                    results.append(package_dict)
                else:
                    pass
        count = query.count
        facets = query.facets
    else:
        count = 0
        facets = {}
        results = []
    search_results = {
        'count': count,
        'facets': facets,
        'results': results,
        'sort': data_dict['sort']
    }
    group_names = []
    for field_name in ('groups', 'organization'):
        group_names.extend(facets.get(field_name, {}).keys())
    groups = (session.query(model.Group.name, model.Group.title)
                    .filter(model.Group.name.in_(group_names))
                    .all()
              if group_names else [])
    group_titles_by_name = dict(groups)
    restructured_facets = {}
    for key, value in facets.items():
        restructured_facets[key] = {
            'title': key,
            'items': []
        }
        for key_, value_ in value.items():
            new_facet_dict = {}
            new_facet_dict['name'] = key_
            if key in ('groups', 'organization'):
                display_name = group_titles_by_name.get(key_, key_)
                display_name = display_name if display_name and display_name.strip() else key_
                new_facet_dict['display_name'] = display_name
            elif key == 'license_id':
                license = model.Package.get_license_register().get(key_)
                if license:
                    new_facet_dict['display_name'] = license.title
                else:
                    new_facet_dict['display_name'] = key_
            else:
                new_facet_dict['display_name'] = key_
            new_facet_dict['count'] = value_
            restructured_facets[key]['items'].append(new_facet_dict)
    search_results['search_facets'] = restructured_facets
    for facet in search_results['search_facets']:
        search_results['search_facets'][facet]['items'] = sorted(
            search_results['search_facets'][facet]['items'],
            key=lambda facet: facet['display_name'], reverse=True)

    return search_results


def group_dictize(group, context, include_groups=True, include_tags=True, include_users=True, include_extras=True,
                  packages_field='datasets', **kw):
    assert packages_field in ('datasets', 'dataset_count', None)
    if packages_field == 'dataset_count':
        dataset_counts = context.get('dataset_counts', None)
    result_dict = d.table_dictize(group, context)
    result_dict.update(kw)
    result_dict['display_name'] = group.title or group.name
    if include_extras:
        result_dict['extras'] = ckan.lib.dictization.model_dictize.extras_dict_dictize(
            group._extras, context)
    context['with_capacity'] = True
    if packages_field:

        def get_packages_for_this_group(group_, just_the_count=False):
            q = {
                'facet': 'false',
                'rows': 0,
            }
            if group_.is_organization:
                q['fq'] = 'owner_org:"{0}"'.format(group_.id)
            else:
                q['fq'] = 'groups:"{0}"'.format(group_.name)
            if group_.is_organization:
                is_group_member = (context.get('user') and
                    authz.has_user_permission_for_group_or_org(
                        group_.id, context.get('user'), 'read'))
                if is_group_member:
                    q['include_private'] = True
            if not just_the_count:
                try:
                    packages_limit = context['limits']['packages']
                except KeyError:
                    q['rows'] = 1000  # Only the first 1000 datasets are returned
                else:
                    q['rows'] = packages_limit
            search_context = dict((k, v) for (k, v) in context.items()
                                  if k != 'schema')
            search_results = package_search(search_context, q)
            return search_results['count'], search_results['results']

        if packages_field == 'datasets':
            package_count, packages = get_packages_for_this_group(group)
            result_dict['packages'] = packages
        else:
            if dataset_counts is None:
                package_count, packages = get_packages_for_this_group(
                    group, just_the_count=True)
            else:
                facets = dataset_counts
                if group.is_organization:
                    package_count = facets['owner_org'].get(group.id, 0)
                else:
                    package_count = facets['groups'].get(group.name, 0)
        result_dict['package_count'] = package_count
    if include_tags:
        result_dict['tags'] = ckan.lib.dictization.model_dictize.tag_list_dictize(
            ckan.lib.dictization.model_dictize._get_members(context, group, 'tags'),
            context)
    if include_groups:
        result_dict['groups'] = ckan.lib.dictization.model_dictize.group_list_dictize(
            ckan.lib.dictization.model_dictize._get_members(context, group, 'groups'),
            context, include_groups=True)
    if include_users:
        result_dict['users'] = ckan.lib.dictization.model_dictize.user_list_dictize(
            ckan.lib.dictization.model_dictize._get_members(context, group, 'users'),
            context)
    context['with_capacity'] = False
    if context.get('for_view'):
        if result_dict['is_organization']:
            plugin = plugins.IOrganizationController
        else:
            plugin = plugins.IGroupController
        for item in plugins.PluginImplementations(plugin):
            result_dict = item.before_view(result_dict)
    image_url = result_dict.get('image_url')
    result_dict['image_display_url'] = image_url
    if image_url and not image_url.startswith('http'):
        image_url = munge.munge_filename_legacy(image_url)
        result_dict['image_display_url'] = helpers.url_for_static(
            'uploads/group/%s' % result_dict.get('image_url'),
            qualified=True
        )
    return result_dict


def get_facet_items_dict(facet, limit=None, exclude_active=False):
    return [{'active': False, 'count': 1, 'display_name': u'org', 'name': u'org'}]


def get_facet_items_dict_org_with_child(facet, limit=None, exclude_active=False):
    return [{'active': False, 'count': 1, 'display_name': u'father', 'name': u'father'},
            {'active': False, 'count': 1, 'display_name': u'child', 'name': u'child'}]


def get_request_param(parameter_name, default=None):
    return None
