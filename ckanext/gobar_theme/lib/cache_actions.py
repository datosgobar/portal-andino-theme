#! coding: utf-8
import requests
import logging

from pylons import config


logger = logging.getLogger(__name__)

def clear_web_cache():
    cache_clean_hook = config.get('andino.cache_clean_hook')
    if cache_clean_hook is not None:
        try:
            response_for_http_request = requests.get(cache_clean_hook, timeout=2)
            response_for_http_request.raise_for_status()
        except Exception as e:
            logger.info(u'Hubo un problema limpiando la caché del servicio web con el request a la url %s: %s ', \
                        cache_clean_hook, e)
