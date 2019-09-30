from urlparse import urljoin

from pydatajson import time_series

from ckanext.gobar_theme.helpers.config import get_from_config_file, get_theme_config


def get_locale_options():
    options = ['AR', 'US']
    return options


def get_series_url_for_field(field):
    if not field_id_can_be_searched(field):
        return ""
    api_uri = get_theme_config('series_tiempo_ar_explorer.series-api-uri') \
              or get_from_config_file('seriestiempoarexplorer.default_series_api_uri')
    api_uri = "{0}{1}".format(api_uri, "" if api_uri.endswith("/") else "/")
    api_uri = urljoin(api_uri, 'series/?ids={}'.format(field.get('id')))
    return api_uri


def field_id_can_be_searched(field):
    return "seriestiempoarexplorer" in get_from_config_file("ckan.plugins") \
           and not field.get('specialType') \
           and time_series.field_is_time_series(field)
