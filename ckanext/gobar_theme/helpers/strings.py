import json
from urlparse import urljoin
from urlparse import urlparse

import ckan.lib.helpers as ckan_helpers
from ckan.common import request
from markdown import markdown
from markupsafe import Markup


def remove_url_param(keys, value=None, replace=None, controller=None,
                     action=None, extras=None, alternative_url=None):
    if isinstance(keys, basestring):
        keys = [keys]
    else:
        keys = keys

    params_nopage = [(k, v) for k, v in request.params.items() if k != 'page']
    params = list(params_nopage)
    if value:
        params.remove((keys[0], value))
    else:
        for key in keys:
            _ = [params.remove((k, v)) for (k, v) in params[:] if k == key]
    if replace is not None:
        params.append((keys[0], replace))
    if alternative_url:
        return ckan_helpers._url_with_params(alternative_url, params)
    return ckan_helpers._create_url_with_params(params=params, controller=controller, action=action, extras=extras)


def cut_text(text, limit):
    if len(text) > limit:
        text, remaining = text[:limit], text[limit:]
        if ' ' in remaining:
            text += remaining.split(' ')[0]
        text += '...'
    return text


def cut_img_path(url):
    return urlparse(url).path


def url_join(base, url, *args):
    return urljoin(base, url, *args)


def json_loads(json_string):
    return json.loads(json_string)


def valid_length(data, max_length):
    return len(data) <= max_length


def capfirst(s):
    return s[0].upper() + s[1:]


def jsondump(field=''):
    return Markup(json.dumps(field))


def convert_plain_string_into_markdown(string):
    return markdown(string)
