import ckan.lib.helpers as ckan_helpers
import ckan.logic as logic


def fetch_groups():
    data_dict_page_results = {
        'all_fields': True,
        'type': 'group',
        'limit': None,
        'offset': 0,
    }
    return logic.get_action('group_list')({}, data_dict_page_results)


def get_faceted_groups(items_limit=None):
    groups = fetch_groups()
    facets = ckan_helpers.get_facet_items_dict(facet='groups', limit=items_limit)
    facets_by_name = {}
    for facet in facets:
        facets_by_name[facet['name']] = facet
    for group in groups:
        group_name = group['name']
        if group_name in facets_by_name:
            group['facet_active'] = facets_by_name[group['name']]['active']
            group['facet_count'] = facets_by_name[group['name']]['count']
        else:
            group['facet_active'] = False
            group['facet_count'] = 0
    return groups


def get_groups_img_paths(groups):
    groups_with_path = {}
    for group in groups:
        groups_with_path[group['id']] = group['image_display_url']
    return groups_with_path


def join_groups(selected_groups):
    data_dict_page_results = {
        'all_fields': True,
        'type': 'group',
        'limit': None,
        'offset': 0,
    }
    groups = logic.get_action('group_list')({}, data_dict_page_results)
    for selected_group in selected_groups:
        for group in groups:
            if selected_group['name'] == group['name']:
                group['selected'] = True
    return sorted(groups, key=lambda k: k['display_name'].lower())
