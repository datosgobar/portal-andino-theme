# coding=utf-8
import json
import os
import re
import urlparse

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import moment
import redis
from ckan.common import request, c
from pylons import config as ckan_config
from ckanext.gobar_theme.lib import cache_actions

parse_params = logic.parse_params
abort = base.abort
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized


class GobArConfigController(base.BaseController):
    # IMG_DIR = '/usr/lib/ckan/default/src/ckanext-gobar-theme/ckanext/gobar_theme/public/user_images/'
    IMG_DIR = '/theme/ckanext/gobar_theme/public/user_images/'
    CONFIG_PATH = '/var/lib/ckan/theme_config/settings.json'

    def edit_title(self):
        self._authorize()
        if request.method == 'POST':

            # Validating the form's fields
            c.errors = {}
            params = parse_params(request.params)
            error_title = (len(params['site-title']) < 9 or len(params['site-title']) > 100)
            error_description = (len(params['site-description']) < 30 or len(params['site-description']) > 300)
            error_organization = (len(params['site-organization']) < 9 or len(params['site-organization']) > 100)
            if error_title:
                c.errors['title_error'] = "Debe contener entre 9 y 100 caracteres!"
            if error_description:
                c.errors['description_error'] = "Debe contener entre 30 y 300 caracteres!"
            if error_organization:
                c.errors['organization_error'] = "Debe contener entre 9 y 100 caracteres!"
            if error_description or error_title or error_organization:
                return base.render('config/config_01_title.html')

            # No errors found within the form's fields --> Modifications will be done
            config_dict = self._read_config()
            new_title_config = {
                'site-title': params['site-title'].strip(),
                'site-description': params['site-description'].strip(),
                'site-organization': params['site-organization'].strip()
            }
            if params['image-logic'] == 'new-image':
                new_title_config['background-image'] = self._save_img(params['background-image'])
            elif params['image-logic'] == 'delete-image':
                new_title_config['background-image'] = None
            else:
                new_title_config['background-image'] = self.get_theme_config('title.background-image')
            config_dict['title'] = new_title_config
            self._set_config(config_dict)
            # Actualizo el data.json
            # Se importa 'datajson_actions' en la función para evitar dependencias circulares con 'config_controller'
            import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
            datajson_actions.enqueue_update_datajson_cache_tasks()
            cache_actions.clear_web_cache()

        return base.render('config/config_01_title.html')

    def edit_home(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['home'] = {
                'title-template': params['title-template']
            }
            self._set_config(config_dict)
        return base.render('config/config_02_home.html')

    def edit_groups(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['groups'] = {
                'imgs': params['group-imgs']
            }
            self._set_config(config_dict)
            if 'json' in params:
                return h.json.dumps({'success': True}, for_json=True)
        return base.render('config/config_03_groups.html')

    def edit_header(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.params)
            config_dict = self._read_config()
            if params['image-logic'] == 'new-image':
                config_dict['header'] = {'image': self._save_img(params['background-image'])}
            elif params['image-logic'] == 'delete-image':
                config_dict['header'] = {'image': None}
            else:
                config_dict['header'] = {'image': self.get_theme_config('header.image')}
            self._set_config(config_dict)
        return base.render('config/config_04_header.html')

    def edit_social(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            if not re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", params['mail'], re.IGNORECASE):
                c.errors = {}
                c.errors['mail_error'] = "El mail es inválido o está incompleto"
                return base.render('config/config_05_social.html')
            config_dict = self._read_config()
            config_dict['social'] = {
                'fb': self._url_with_protocol(params['fb'].strip()),
                'tw': self._url_with_protocol(params['tw'].strip()),
                'github': self._url_with_protocol(params['github'].strip()),
                'inst': self._url_with_protocol(params['inst'].strip()),
                'yt': self._url_with_protocol(params['yt'].strip()),
                'mail': params['mail'].strip()
            }
            self._set_config(config_dict)
        import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
        datajson_actions.enqueue_update_datajson_cache_tasks()
        cache_actions.clear_web_cache()

        return base.render('config/config_05_social.html')

    def edit_footer(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.params)
            new_footer_params = {'url': self._url_with_protocol(params['url'].strip())}
            if params['image-logic'] == 'new-image':
                new_footer_params['image'] = self._save_img(params['background-image'])
            elif params['image-logic'] == 'delete-image':
                new_footer_params['image'] = None
            else:
                new_footer_params['image'] = self.get_theme_config('footer.image')
            config_dict = self._read_config()
            config_dict['footer'] = new_footer_params
            self._set_config(config_dict)
        return base.render('config/config_06_footer.html')

    def edit_datasets(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['dataset'] = {
                'description': params['dataset-description'].strip()
            }
            self._set_config(config_dict)
        return base.render('config/config_07_dataset.html')

    def edit_organizations(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['organization'] = {
                'description': params['organization-description'].strip(),
                'show-organizations': 'show-organizations' in params
            }
            self._set_config(config_dict)
        return base.render('config/config_08_organizations.html')

    def edit_about(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            try:
                new_sections = [params.get('about-sections')]
                json_sections = json.loads(new_sections[0])
            except ValueError:  # no se envió ningún JSON (no se usa el tipo avanzado de 'Acerca')
                json_sections = []
            config_dict['about'] = {
                'title': params['about-title'].strip(),
                'description': params['about-description'].strip(),
                'about-type': params['about-type'],
                'sections': (json_sections or []),
            }
            self._set_config(config_dict)
        return base.render('config/config_09_about.html')

    def edit_metadata_google_fb(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            new_metadata_config = {
                'title': params['metadata-title'].strip(),
                'description': params['metadata-description'].strip()
            }
            if params['image-logic'] == 'new-image':
                new_metadata_config['image'] = self._save_img(params['image'])
            elif params['image-logic'] == 'delete-image':
                new_metadata_config['image'] = None
            else:
                new_metadata_config['image'] = self.get_theme_config('fb-metadata.image')
            config_dict['fb-metadata'] = new_metadata_config
            self._set_config(config_dict)
        return base.render('config/config_10_metadata_google_fb.html')

    def edit_metadata_tw(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            new_metadata_config = {
                'title': params['metadata-title'].strip(),
                'description': params['metadata-description'].strip(),
                'user': params['metadata-user'].strip()
            }
            if params['image-logic'] == 'new-image':
                new_metadata_config['image'] = self._save_img(params['image'])
            elif params['image-logic'] == 'delete-image':
                new_metadata_config['image'] = None
            else:
                new_metadata_config['image'] = self.get_theme_config('tw-metadata.image')
            config_dict['tw-metadata'] = new_metadata_config
            self._set_config(config_dict)
        return base.render('config/config_11_metadata_twitter.html')

    def edit_metadata_portal(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()

            languages = params.get('metadata-languages', [])
            if not isinstance(languages, list):
                languages = [languages]

            new_metadata_config = {
                'homepage': params['metadata-homepage'].strip(),
                'id': params['metadata-id'].strip(),
                'launch_date': params['metadata-launch_date'],
                'licence_conditions': params['metadata-licence_conditions'].strip(),
                'languages': languages,
                'last_updated': moment.now().isoformat(),
                'license': params['metadata-license'].strip(),
                'country': params['metadata-country'].strip(),
                'province': params['metadata-province'].strip(),
                'districts': params.get('metadata-municipio', []),
            }
            config_dict['portal-metadata'] = new_metadata_config
            self._set_config(config_dict)
            # Actualizo el data.json
            # Se importa 'datajson_actions' en la función para evitar dependencias circulares con 'config_controller'
            import ckanext.gobar_theme.lib.datajson_actions as datajson_actions
            datajson_actions.enqueue_update_datajson_cache_tasks()
            cache_actions.clear_web_cache()
        return base.render(template_name='config/config_12_metadata_portal.html')

    def edit_apis(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['apis'] = {
                'description': params['apis-description'].strip(),
                'show-apis': 'show-apis' in params
            }
            self._set_config(config_dict)
        return base.render('config/config_13_apis.html')

    def edit_greetings(self):
        self._authorize()
        if request.method == 'POST':
            config_dict = self._read_config()
            config_dict['show-greetings'] = False
            self._set_config(config_dict)
        return h.json.dumps({'success': True}, for_json=True)

    @staticmethod
    def _url_with_protocol(url):
        url = url.strip()
        if len(url) > 0 and not urlparse.urlparse(url).scheme:
            url = "http://" + url
        return url

    @staticmethod
    def _authorize():
        context = {'model': model, 'user': c.user, 'auth_user_obj': c.userobj}
        try:
            logic.check_access('sysadmin', context, {})
            return True
        except logic.NotAuthorized:
            return h.redirect_to('home')

    @classmethod
    def _read_config(cls):
        try:
            andino_config = cls._redis_cli().get('andino-config')
            gobar_config = json.loads(andino_config)
        except Exception:
            with open(GobArConfigController.CONFIG_PATH) as json_data:
                try:
                    gobar_config = json.load(json_data)
                except Exception:
                    gobar_config = {}
                cls._redis_cli().set('andino-config', json.dumps(gobar_config))

        return gobar_config

    @classmethod
    def _set_config(cls, config_dict):
        json_string = json.dumps(config_dict, sort_keys=True, indent=2)
        cls._redis_cli().set('andino-config', json_string)
        with open(GobArConfigController.CONFIG_PATH, 'w') as json_data:
            json_data.write(json_string)

    @classmethod
    def get_theme_config(cls, path=None, default=None):
        gobar_config = cls._read_config()
        if path is not None:
            keys = path.split('.')
            for key in keys:
                if gobar_config is not None and key in gobar_config:
                    gobar_config = gobar_config[key]
                else:
                    gobar_config = default
        return gobar_config

    @classmethod
    def _save_img(cls, field_storage):
        output_path = os.path.join(cls.IMG_DIR, field_storage.filename)
        output_file = open(output_path, 'wb')
        upload_file = field_storage.file
        upload_file.seek(0)
        while True:
            data = upload_file.read(2 ** 20)
            if not data:
                break
            output_file.write(data)
        output_file.close()
        return os.path.join('/user_images/', field_storage.filename)

    @classmethod
    def _redis_cli(cls):
        if not getattr(cls, '_redis', None):
            redis_url = ckan_config.get('ckan.redis.url')
            pr = urlparse.urlparse(redis_url)
            db = os.path.basename(pr.path)

            cls._redis = redis.StrictRedis(host=pr.hostname, port=pr.port, db=db)

        return cls._redis
