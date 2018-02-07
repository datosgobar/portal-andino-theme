#! coding: utf-8
import json
import os

from ckan.lib.base import BaseController, response, request, c

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

    def localidades(self):
        response.content_type = 'application/json'
        
        province_id = None
        if 'provincia_id' in request.params.keys():
            province_id = request.params.get('provincia_id')

        with open(os.path.join(GobArSpatialController.SITE_ROOT, 'resources/localidades.json')) as file_handle:
            districts = json.loads(file_handle.read())

            if province_id:
                output_dict = [district for district in districts['localidades'] if district['provincia_id'] == province_id]
                districts['localidades'] = output_dict

            return json.dumps(districts)
