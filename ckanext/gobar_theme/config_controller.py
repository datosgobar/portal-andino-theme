# coding=utf-8
import json
import logging
import os
import re
import urlparse

import moment
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
from ckan.common import request, c
from pylons import config

from ckanext.gobar_theme.lib import cache_actions
from ckanext.gobar_theme.theme_config import ThemeConfig
from .utils.ckan_utils import plugin_or_404, TS_EXPLORER_PLUGIN

parse_params = logic.parse_params
abort = base.abort
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized
logger = logging.getLogger(__name__)


class GobArConfigController(base.BaseController):
    IMG_DIR = '/usr/lib/ckan/default/src/ckanext-gobar-theme/ckanext/gobar_theme/public/user_images/'
    CONFIG_PATH = '/var/lib/ckan/theme_config/settings.json'

    def __init__(self):
        super(GobArConfigController, self).__init__()
        self.config = ThemeConfig(self.CONFIG_PATH)

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
            if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", params['mail'], re.IGNORECASE):
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
                'linkedin': self._url_with_protocol(params['linkedin'].strip()),
                'blog': self._url_with_protocol(params['blog'].strip()),
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

    def edit_series(self):
        from ckanext.gobar_theme.helpers import get_default_series_api_url
        plugin_or_404(TS_EXPLORER_PLUGIN)
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['series_tiempo_ar_explorer'] = {
                'featured': params['featured'].strip(),
                'enable': 'enable' in params,
                'series-api-uri': params['series-api-uri'] or get_default_series_api_url(),
                'laps': self.generate_laps_json(params),
                'locale': params['locale'].strip(),
                'format-chart-units': 'format-chart-units' in params,
                'max-decimals': params['max-decimals'].strip()
            }
            # Seteo la imagen de fondo del Explorer
            if params['image-logic'] == 'new-image':
                config_dict['series_tiempo_ar_explorer']['hero-image-url'] = self._save_img(params['background-image'])
            elif params['image-logic'] == 'delete-image':
                config_dict['series_tiempo_ar_explorer']['hero-image-url'] = None
            else:
                config_dict['series_tiempo_ar_explorer']['hero-image-url'] = \
                    self.get_theme_config('series_tiempo_ar_explorer')['hero-image-url']

            self._set_config(config_dict)
        return base.render('config/config_14_series.html')

    def edit_google_dataset_search(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['google_dataset_search'] = {
                'enable_structured_data': 'enable_structured_data' in params
            }
            self._set_config(config_dict)
        return base.render('config/config_15_google_dataset_search.html')

    def edit_datastore_commands(self):
        if 'datapusher' in config.get('ckan.plugins', ''):
            plugin_command = '--plugin=ckan datapusher submit_all'
        elif 'xloader' in config.get('ckan.plugins', ''):
            plugin_command = '--plugin=ckanext-xloader xloader submit all'
        else:
            return h.redirect_to('home')
        self._authorize()
        if request.method == 'POST':
            from ckanext.gobar_theme.helpers.cron import create_or_update_cron_job
            params = parse_params(request.POST)
            config_dict = self._read_config()
            schedule_hour = params.get('schedule-hour').strip()
            schedule_minute = params.get('schedule-minute').strip()
            config_dict['datastore'] = {
                'schedule-hour': schedule_hour,
                'schedule-minute': schedule_minute
            }
            self._set_config(config_dict)
            # Creamos el cron job, reemplazando el anterior si ya existía
            command = self._generate_datastore_command(plugin_command)
            comment = 'datastore - submit_all'
            create_or_update_cron_job(command, hour=schedule_hour, minute=schedule_minute, comment=comment)
        return base.render('config/config_18_datastore_commands.html')

    def edit_google_tag_manager(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['google_tag_manager'] = {
                'container-id': params['container-id'].strip()
            }
            self._set_config(config_dict)
        return base.render('config/config_16_google_tag_manager.html')

    def edit_greetings(self):
        self._authorize()
        if request.method == 'POST':
            config_dict = self._read_config()
            config_dict['show-greetings'] = False
            self._set_config(config_dict)
        return h.json.dumps({'success': True}, for_json=True)

    def edit_login_title(self):
        self._authorize()
        if request.method == 'POST':
            params = parse_params(request.POST)
            config_dict = self._read_config()
            config_dict['login-title'] = params['login-title'].strip()
            self._set_config(config_dict)
        return base.render('config/config_19_login_title.html')

    def _generate_datastore_command(self, plugin_command):
        paster_path = self.get_paster_path()
        paster_config = '-y -c {}'.format(self.get_config_file_path())
        submit_command = '{0} {1} {2}'.format(paster_path, plugin_command, paster_config)
        create_views_command = '{0} --plugin=ckan views create {1}'.format(paster_path, paster_config)
        return '{0} && {1}'.format(submit_command, create_views_command)

    @staticmethod
    def _url_with_protocol(url):
        url = url.strip()
        if url and not urlparse.urlparse(url).scheme:
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

    def _read_config(self):
        return self.config.get_all()

    def _set_config(self, config_dict):
        return self.config.set_new_config(config_dict)

    def get_theme_config(self, path=None, default=None):
        return self.config.get(path, default)

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

    def get_config_file_path(self):
        return "{}/production.ini".format(os.getenv('CKAN_DEFAULT').strip())

    def get_paster_path(self):
        return "{}/bin/paster".format(os.getenv('CKAN_HOME').strip())

    def generate_laps_json(self, params):
        return {
            'diaria': params['diaria'].strip(),
            'mensual': params['mensual'].strip(),
            'trimestral': params['trimestral'].strip(),
            'semestral': params['semestral'].strip(),
            'anual': params['anual'].strip()
        }
