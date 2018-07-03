import requests


def clear_web_cache(url):
    try:
        response_for_http_request = requests.get(url, timeout=2)
        response_for_http_request.raise_for_status()
    except requests.exceptions.HTTPError:
        # Hubo un problema con el request
        pass
