#! coding: utf-8
import json
import os

from ckan.lib.base import BaseController, response, request


class GobArSpatialController(BaseController):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

    def paises(self):
        response.content_type = 'application/json'
        with open(os.path.join(GobArSpatialController.SITE_ROOT, 'resources/paises.json')) as file_handle:
            return file_handle.read()

    def provincias(self):
        response.content_type = 'application/json'
        with open(os.path.join(GobArSpatialController.SITE_ROOT, 'resources/provincias.json')) as file_handle:
            return file_handle.read()

    def __local_administrative_unit(self, file_name, administrative_unit_name):
        response.content_type = 'application/json'

        province_ids = []
        if 'provincia_id' in request.params.keys() and request.params.get('provincia_id'):
            province_ids = request.params.get('provincia_id')
            if not isinstance(province_ids, list):
                province_ids = province_ids.split(',')

        with open(os.path.join(GobArSpatialController.SITE_ROOT, 'resources/%s' % file_name)) as file_handle:
            districts = json.loads(file_handle.read())

            if province_ids:
                output_dict = [district for district in districts[administrative_unit_name] if
                               district['provincia_id'] in province_ids]
                districts[administrative_unit_name] = output_dict

            return json.dumps(districts)

    def localidades(self):
        return self.__local_administrative_unit('localidades.json', 'localidades')

    def municipios(self):
        return self.__local_administrative_unit('municipios.json', 'municipios')
