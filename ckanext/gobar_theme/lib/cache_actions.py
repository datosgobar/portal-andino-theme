from pylons import config
import requests
import logging

logger = logging.getLogger(__name__)

def clear_web_cache():
    cache_clean_hook = config.get('andino.cache_clean_hook')
    if cache_clean_hook is not None:
        try:
            response_for_http_request = requests.get(cache_clean_hook, timeout=2)
            response_for_http_request.raise_for_status()
        except requests.exceptions.HTTPError:
            logger.info('Hubo un problema con el request a la url ' + cache_clean_hook)
