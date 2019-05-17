import ckan.lib.formatters as formatters
from urlparse import urlparse
from ckan.common import c, config as cconfig, is_flask_request
from ckan.lib.helpers import are_there_flash_messages, url_for, is_url
from flask import redirect as _flask_redirect
from routes import redirect_to as _routes_redirect_to
from webhelpers.html import literal
from routes import request_config, url_for as rurl_for


def redirect_to(*args, **kw):
    if are_there_flash_messages():
        kw['__no_cache__'] = True

    # Routes router doesn't like unicode args
    uargs = map(lambda arg: str(arg) if isinstance(arg, unicode) else arg, args)

    # _url = ''
    # skip_url_parsing = False
    # parse_url = kw.pop('parse_url', False)
    # if uargs and len(uargs) is 1 and isinstance(uargs[0], basestring) and (uargs[0].startswith('/') or is_url(uargs[0])) and parse_url is False:
    #     skip_url_parsing = True
    #     _url = uargs[0]
    #
    # if skip_url_parsing is False:
    #     _url = url_for(*uargs, **kw)
    #
    # if _url.startswith('/'):
    #     _url = urlparse(c.pylons.request.url).netloc or str(config['ckan.site_url'].rstrip('/')) + _url
    #     _url = urlparse(c.pylons.request.url).netloc or str(config['ckan.site_url'].rstrip('/'))

    # _url = '/'  # Usando '/', se queda en 0.0.0.0
    # if is_flask_request():
    #     return _flask_redirect(_url)
    # else:
    #     return _routes_redirect_to(_url)


    _url = '/'
    skip_url_parsing = False
    parse_url = kw.pop('parse_url', False)
    if uargs and len(uargs) is 1 and isinstance(uargs[0], basestring) and (uargs[0].startswith('/') or is_url(uargs[0])) and parse_url is False:
        skip_url_parsing = True
        _url = uargs[0]

    if skip_url_parsing is False:
        _url = url_for(*uargs, **kw)

    if _url.startswith('/'):
        _url = str(cconfig['ckan.site_url'].rstrip('/') + _url)
    if is_flask_request():
        return _flask_redirect(_url)
    else:
        target = rurl_for('/')
        config = request_config()
        return config.redirect(target)
