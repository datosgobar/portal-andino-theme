#! coding: utf-8

from ckan.lib.base import BaseController
import ckanext.gobar_theme.lib.datajson_actions as datajson_actions


class GobArDatajsonController(BaseController):

    def datajson(self):
        return datajson_actions.get_data_json_contents()

    def generate_xlsx(self):
        return datajson_actions.get_catalog_xlsx()
