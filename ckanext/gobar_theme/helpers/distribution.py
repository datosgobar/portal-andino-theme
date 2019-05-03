#!coding=utf-8
import logging
from HTMLParser import HTMLParser

from pydatajson import DataJson
from pylons import config as config

from ckanext.gobar_theme.utils.data_json_utils import get_data_json_contents

logger = logging.getLogger(__name__)

def get_distribution_metadata(resource_id):
    # Se importa 'datajson_actions' en la función para evitar dependencias circulares con 'config_controller'
    json_dict = get_data_json_contents()
    html_parser = HTMLParser()
    json_dict = html_parser.unescape(json_dict)
    datajson = DataJson(json_dict)
    dist = datajson.get_distribution(resource_id)
    return dist


def is_distribution_local(distribution_metadata):
    ckan_site_url = config.get('ckan.site_url')
    try:
        accessURL = distribution_metadata.get('accessURL', '')
        return accessURL.startswith(ckan_site_url)
    except AttributeError:
        logger.error("Se intentó buscar información de un recurso que no figura en el data.json")
    return False


def get_extra_value(extras_list, field):
    for extra_field in extras_list:
        if extra_field['key'] == field:
            return extra_field['value']
    return None


def get_distribution_id():
    return get_data_json_contents().get('identifier') or ''
