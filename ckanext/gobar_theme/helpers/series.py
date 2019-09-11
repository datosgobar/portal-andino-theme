import json
import requests
import urllib2
from pydatajson import time_series
from urlparse import urljoin

from ckanext.gobar_theme.helpers.config import get_from_config_file, get_theme_config


def get_series_url_for_field(field):
    if field_id_can_be_searched(field):
        api_uri = get_theme_config('series_tiempo_ar_explorer.series-api-uri') \
                  or get_from_config_file('seriestiempoarexplorer.default_series_api_uri')
        api_uri = "{0}{1}".format(api_uri, "" if api_uri.endswith("/") else "/")
        api_uri = urljoin(api_uri, 'series/?ids={}'.format(field.get('id')))
        # response = requests.head(api_uri)
        # if response.status_code == 200:
        return api_uri
    return ""


def field_id_can_be_searched(field):
    return "seriestiempoarexplorer" in get_from_config_file("ckan.plugins") \
           and not field.get('specialType') \
           and time_series.field_is_time_series(field)
