#! coding: utf-8

from pylons import response
from ckan.lib.base import BaseController

import ckanext.gobar_theme.lib.datajson_actions as datajson_actions


class GobArDatajsonController(BaseController):

    def datajson(self):
        response.content_type = 'application/json; charset=UTF-8'
        return datajson_actions.get_data_json_contents()

    def catalog_xlsx(self):
        response.content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return datajson_actions.get_catalog_xlsx()
