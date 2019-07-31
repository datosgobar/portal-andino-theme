#!coding=utf-8
from datetime import time
from dateutil import parser, tz

import moment

import ckan.lib.formatters as formatters
import ckan.lib.helpers as ckan_helpers
from ckan.common import _


def convert_iso_string_to_utc(date_string=''):
    if date_string is None:
        return ''
    try:
        date_time = parser.parse(date_string)
    except ValueError:
        # date_string es un string inválido o None
        return ''
    if date_time.time() == time(0):
        return date_string
    if date_time.tzinfo is not None:
        utc_date_time = date_time.astimezone(tz.tzutc())
    else:
        utc_date_time = date_time
    utc_date_time = utc_date_time.replace(tzinfo=None)
    return utc_date_time.isoformat()


def date_format_to_iso(date):
    if date:
        return moment.date(date, "%d/%m/%Y").isoformat()
    return date


def render_ar_datetime(datetime_):
    datetime_ = ckan_helpers._datestamp_to_datetime(convert_iso_string_to_utc(datetime_))
    if not datetime_:
        return ''
    return _('{day} de {month} de {year}').format(
        year=datetime_.year,
        month=formatters._MONTH_FUNCTIONS[datetime_.month - 1]().lower(),
        day=datetime_.day)
