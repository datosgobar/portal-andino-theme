import json
import logging
import os
import urlparse

import redis
from pylons import config as ckan_config

logger = logging.getLogger(__name__)


class ThemeConfig(object):
    def __init__(self, settings_file_path, redis_key='andino-config'):
        self.settings_path = settings_file_path
        self.redis_config_key = redis_key
        self._redis = self._init_redis()

    def get(self, key, default=None):
        gobar_config = self._read_config()

        for item in key.split('.'):
            if item not in gobar_config:
                return default
            gobar_config = gobar_config.get(item, default)

        return gobar_config

    def get_all(self):
        return self._read_config()

    def set(self, key, value):
        config = self._read_config()
        config[key] = value
        self._set_config(config)

    def set_new_config(self, new_config):
        self._set_config(new_config)

    def _set_config(self, config_dict):
        json_string = json.dumps(config_dict, sort_keys=True, indent=2)
        self._redis.set(self.redis_config_key, json_string)
        with open(self.settings_path, 'w') as json_data:
            json_data.write(json_string)

    def _read_config(self):
        try:
            andino_config = self._redis.get(self.redis_config_key)
            gobar_config = json.loads(andino_config)
        except Exception:
            try:
                with open(self.settings_path) as json_data:
                    gobar_config = json.load(json_data)
            except Exception:
                gobar_config = {}
            try:
                self._redis.set(self.redis_config_key, json.dumps(gobar_config))
            except Exception:
                logger.error("Redis no se encuentra disponible!")
        return gobar_config

    def _init_redis(self):
        redis_url = ckan_config.get('ckan.redis.url')
        pr = urlparse.urlparse(redis_url)
        db = os.path.basename(pr.path)

        return redis.StrictRedis(host=pr.hostname, port=pr.port, db=db)
