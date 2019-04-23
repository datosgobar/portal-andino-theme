import json


def get_data_json_contents():
    import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
    return json.loads(datajson_actions.get_data_json_contents())


def get_distribution_id():
    return get_data_json_contents().get('identifier') or ''
