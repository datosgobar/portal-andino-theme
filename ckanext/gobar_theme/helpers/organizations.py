#!coding=utf-8
import ckan.lib.helpers as ckan_helpers
import ckan.lib.search as search
import ckan.logic as logic


def _get_organizations_objs(organizations_branch, depth=0):
    organizations = []
    for tree_obj in organizations_branch:
        organization = ckan_helpers.get_organization(org=tree_obj['name'])
        organization['depth'] = depth
        if 'children' in tree_obj and tree_obj['children']:
            organization['children'] = _get_organizations_objs(tree_obj['children'], depth=depth + 1)
        organizations.append(organization)
    return organizations


def _count_total(organization):
    children_count = 0
    if 'children' in organization and organization['children']:
        for child_organization in organization['children']:
            children_count += _count_total(child_organization)
    return organization['package_count'] + children_count


def organizations_basic_info(separate_children_from_parents=False):
    def convert_organization_to_dict(organization, depth):
        current_organization = {}
        organization_id = organization.pop('id')
        current_organization['id'] = organization_id
        current_organization['name'] = organization.pop('name')
        current_organization['title'] = organization.pop('title')
        current_organization['depth'] = depth  # si depth == 0, la organización no es hija de otra
        current_organization['own_package_count'] = organizations_that_have_packages.pop(organization_id, 0)
        own_available_package_count = ckan_organizations_info.pop(current_organization['name'], {}).get('count', 0)
        children_data_dict = generate_children_data(organization.pop('children'), depth)
        current_organization['children'] = children_data_dict['dict_children']
        current_organization['total_package_count'] = children_data_dict['current_total_package_count'] \
                                                      + current_organization['own_package_count']
        current_organization['available_package_count'] = children_data_dict['current_available_package_count'] + \
                                                          own_available_package_count
        current_organization['active'] = current_organization['name'] == organization_in_request
        current_organization['display'] = not organization_in_request or current_organization['active']
        return current_organization

    def generate_children_data(group_tree_children, depth):
        dict_children = []
        current_available_package_count = 0
        current_total_package_count = 0
        for child in group_tree_children:
            converted_child = convert_organization_to_dict(child, depth + 1)
            dict_children.append(converted_child)
            current_available_package_count += converted_child.get('available_package_count', 0)
            current_total_package_count += converted_child.get('total_package_count', 0)
        return {'dict_children': dict_children, 'current_available_package_count': current_available_package_count,
                'current_total_package_count': current_total_package_count}

    # Traemos las organizaciones
    organizations = get_organizations_tree()
    ckan_organizations_info = {item['name']: item for item in ckan_helpers.get_facet_items_dict('organization')}

    # Realizamos una query para conseguir las organizaciones que tienen datasets, y la cantidad de éstos
    query = search.PackageSearchQuery()
    q = {'q': '+capacity:public', 'fl': 'groups', 'facet.field': ['groups', 'owner_org'], 'facet.limit': -1, 'rows': 1}
    query.run(q)
    organizations_that_have_packages = query.facets.get('owner_org')

    # Transformamos cada organización en un dict para facilitar su uso, y agregamos información requerida
    organizations_data = []
    organization_in_request = ckan_helpers.get_request_param('organization')
    for organization in organizations:
        current_organization = convert_organization_to_dict(organization, 0)
        organizations_data.append(current_organization)

    if separate_children_from_parents:
        return organizations_info_with_children_as_separate(organizations_data)
    return organizations_data


def get_organizations_tree():
    return logic.get_action('group_tree')({}, {'type': 'organization'})


def organization_tree():
    organizations_tree = logic.get_action('group_tree')({}, {'type': 'organization'})
    organizations = _get_organizations_objs(organizations_tree)
    for organization in organizations:
        organization['display_count'] = _count_total(organization)
    return organizations


def get_complete_organization_from_tree(name, search_suborganizations=False):
    orgs = organizations_basic_info(separate_children_from_parents=search_suborganizations)
    for organization in orgs:
        if organization.get('name') == name:
            return organization
    return None


def organizations_with_packages():
    organizations = logic.get_action('organization_list')({}, {'all_fields': True})
    organizations_with_at_least_one_package = [
        organization for organization in organizations if organization['package_count'] > 0
    ]
    return len(organizations_with_at_least_one_package)


def get_pkg_extra(pkg, keyname):
    if 'extras' in pkg and pkg['extras']:
        for extra in pkg['extras']:
            if extra['key'] == keyname:
                return extra['value']
    return None


def organizations_info_with_children_as_separate(organizations):
    all_organizations = []
    for organization in organizations:
        children = organization.get('children', [])
        if children:
            for child in children:
                child['parent_name'] = organization['name']
            all_organizations.extend(organizations_info_with_children_as_separate(children))
        all_organizations.append(organization)
    return all_organizations
