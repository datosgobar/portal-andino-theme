#! coding: utf-8
import cgi
import os

import pylons
from ckan.lib import uploader

from ckanext.gobar_theme.config_controller import GobArConfigController

config = pylons.config

_storage_path = None
_ufs = None


class GobArThemeResourceUploader(uploader.ResourceUpload):

    def __init__(self, data_dict):
        super(GobArThemeResourceUploader, self).__init__(data_dict)

        # Cuando se edita un recurso, queremos asegurarnos de que el campo 'url_type' tenga el valor correcto
        resource_has_uploaded_file = data_dict.get('has-uploaded-file', '')
        if resource_has_uploaded_file == 'upload':
            data_dict['url_type'] = 'upload'
        if resource_has_uploaded_file in data_dict.keys():
            data_dict.pop('has-uploaded-file')

        # Hacer el init para el ícono `icon_upload`

        resource_id = data_dict.get('id')
        icon_upload_field_storage = data_dict.pop('icon_upload', None)
        self.icon_clear = data_dict.pop('clear_icon_upload', None)

        if isinstance(icon_upload_field_storage, cgi.FieldStorage):
            self.icon_filename = '%s-%s' % (resource_id, icon_upload_field_storage.filename)
            self.icon_upload_file = icon_upload_field_storage.file

            data_dict['icon_url'] = config.get('ckan.site_url') + '/user_images/%s' % self.icon_filename
            data_dict['icon_url_type'] = 'upload'
        elif self.icon_clear:
            data_dict['icon_url_type'] = ''

    # pylint: disable=W0622
    def upload(self, id, max_size=10):
        super(GobArThemeResourceUploader, self).upload(id, max_size)

        if not hasattr(self, 'icon_filename'):
            return

        # Hacer el upload para el ícono
        output_path = os.path.join(GobArConfigController.IMG_DIR, self.icon_filename)
        output_file = open(output_path, 'wb')
        upload_file = self.icon_upload_file
        write_file_to_output_buffer(upload_file, output_file)


def write_file_to_output_buffer(input_file, output_file):
    input_file.seek(0)
    while True:
        data = input_file.read(2 ** 20)
        if not data:
            break
        output_file.write(data)
    output_file.close()
