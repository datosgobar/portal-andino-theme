# coding=utf-8
import logging
import re
import sys

import ckan
import ckan.lib.activity_streams as activity_streams
import ckan.lib.base as base
import ckan.logic as logic
import pkg_resources
from webhelpers.html import literal

import ckanext
from ckanext.gobar_theme.helpers import get_gobar_activity_streams, get_complete_organization_from_tree
from ckanext.gobar_theme.utils.andino_version import get_portal_andino_version
from . import helpers as h

_get_action = ckan.logic.get_action
logger = logging.getLogger(__name__)


def package_activity_list_html(context, data_dict):
    activity_stream = logic.action.get.package_activity_list(context, data_dict)
    offset = int(data_dict.get('offset', 0))
    extra_vars = {
        'controller': 'package',
        'action': 'activity',
        'id': data_dict['id'],
        'offset': offset,
    }
    return activity_list_to_html(
        context, activity_stream, extra_vars)


def activity_list_to_html(context, activity_stream, extra_vars):
    activity_list = []  # These are the activity stream messages.
    for activity in activity_stream:
        detail = None
        activity_type = activity['activity_type']
        if activity_type not in activity_streams.activity_stream_string_functions \
                and activity_type not in get_gobar_activity_streams():
            raise NotImplementedError("No activity renderer for activity type '%s'" % activity_type)

        # Some activity types may have details.
        result = get_activity_context(activity, activity_type, context, detail)

        reload(sys)
        sys.setdefaultencoding('utf-8')
        if result:
            activity_list.append(result)

        extra_vars['activities'] = activity_list
    return literal(base.render('activity_streams/activity_stream_items.html',
                               extra_vars=extra_vars))


# pylint:disable=too-many-branches
def get_activity_context(activity, activity_type, context, detail):
    if activity_type in activity_streams.activity_stream_actions_with_detail:
        details = logic.get_action('activity_detail_list')(context=context,
                                                           data_dict={'id': activity['id']})
        # If an activity has just one activity detail then render the
        # detail instead of the activity.
        if len(details) == 1:
            detail = details[0]
            object_type = detail['object_type']

            if object_type == 'PackageExtra':
                object_type = 'package_extra'

            new_activity_type = '%s %s' % (detail['activity_type'],
                                           object_type.lower())
            if new_activity_type in activity_streams.activity_stream_string_functions:
                activity_type = new_activity_type
    if activity_type in activity_streams.activity_stream_string_icons:
        activity_icon = activity_streams.activity_stream_string_icons[activity_type]
    else:
        activity_icon = activity_streams.activity_stream_string_icons['undefined']

    if activity_type in get_gobar_activity_streams():
        activity_msg = get_gobar_activity_streams().get(activity_type)()
    else:
        activity_msg = activity_streams.activity_stream_string_functions[activity_type](context, activity)
    # Get the data needed to render the message.
    matches = re.findall(r'{([^}]*)}', activity_msg)
    data = {}
    for match in matches:
        snippet = activity_streams.activity_snippet_functions[match](activity, detail)
        if match == 'extra':
            if 'updateFrequency' in snippet:
                data[str(match)] = 'Frecuencia de actualización'
                activity_msg = u'{actor} actualizó {extra} del conjunto de datos {dataset}'
            else:
                return {}
        else:
            data[str(match)] = snippet
    result = {'msg': activity_msg,
              'type': activity_type.replace(' ', '-').lower(),
              'icon': activity_icon,
              'data': data,
              'timestamp': activity['timestamp'],
              'is_new': activity.get('is_new', False)}
    return result


def _resource_purge(context, data_dict):
    model = context['model']
    _id = ckan.logic.get_or_bust(data_dict, 'id')
    entity = model.Resource.get(_id)
    entity.purge()
    model.repo.commit_and_remove()


def _resource_delete_from_datastore(context, data_dict):
    _id = ckan.logic.get_or_bust(data_dict, 'id')
    ckanext.datastore.logic.action.datastore_delete(context, {'resource_id': _id, 'force': True})


def resource_delete_and_purge(context, data_dict):
    try:
        _resource_delete_from_datastore(context, data_dict)
    except logic.NotFound:
        logger.warning("Se produjo un error buscando el recurso en DataStore ( id = %s)", data_dict['id'])
        # TODO: arreglar este logeo, no funciona
    logic.action.delete.resource_delete(context, data_dict)
    _resource_purge(context, data_dict)


def group_delete_and_purge(context, data_dict):
    logic.action.delete._group_or_org_delete(context, data_dict)
    return logic.action.delete.group_purge(context, data_dict)


def _delete_and_purge_datasets_resources(context, data_dict):
    resources = logic.action.get.package_show(context, data_dict)['resources']
    for resource in resources:
        resource_delete_and_purge(context, {'id': resource['id']})


def dataset_delete_and_purge(context, data_dict):
    logic.action.delete.package_delete(context, data_dict)
    _delete_and_purge_datasets_resources(context, data_dict)
    return logic.action.delete.dataset_purge(context, data_dict)


def organization_delete_and_purge(context, data_dict):
    organization = get_complete_organization_from_tree(data_dict.get('id'), search_suborganizations=True)
    dataset_count_from_organization_and_children = organization.get('total_package_count')
    if dataset_count_from_organization_and_children > 0:
        raise ValueError('Se contaron {} datasets que pertenecen a esta organización y las que '
                         'dependen de ella. Por favor, borralos.'.format(dataset_count_from_organization_and_children))
    return _delete_and_purge_organization_and_children(context, data_dict, organization)


def _delete_and_purge_organization_and_children(context, data_dict, organization):
    for suborganization in organization.get('children'):
        _delete_and_purge_organization_and_children(context, {'id': suborganization.get('name')}, suborganization)
    logic.action.delete._group_or_org_delete(context, data_dict, is_org=True)
    return logic.action.delete.group_purge(context, data_dict)


def gobar_status_show(_context, _data_dict):
    artifacts = []
    plugins = ['ckanext-gobar-theme', 'ckanext-hierarchy']
    for plugin in plugins:
        version = _get_plugin_version(plugin)
        artifact = {plugin: version}
        artifacts.append(artifact)
    portal_andino_version = get_portal_andino_version()
    artifacts.append({'portal-andino': portal_andino_version})
    return artifacts


def _get_plugin_version(plugin):
    try:
        version = pkg_resources.require(plugin)[0].version
    except Exception:
        version = None
    return version


def activity_create(context, activity_dict):
    logic.check_access('activity_create', context, activity_dict)
    model = context['model']
    activity_dict['revision_id'] = None
    activity_obj = model.Activity(activity_dict['user_id'],
                                  activity_dict['object_id'],
                                  activity_dict['revision_id'],
                                  activity_dict['activity_type'],
                                  None)
    activity_obj.save()
    if not context.get('defer_commit'):
        model.repo.commit()
