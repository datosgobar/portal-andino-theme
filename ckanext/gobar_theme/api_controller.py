#!coding: utf-8
import json

import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
from ckan.common import c
from ckan.controllers.api import ApiController
from ckanext.googleanalytics.controller import GAApiController


class GobArApiController(GAApiController, ApiController):

    def _remove_extra_id_field(self, json_string):
        json_dict = json.loads(json_string)
        has_extra_id = False
        if 'result' in json_dict and 'fields' in json_dict['result']:
            for field in json_dict['result']['fields']:
                if 'id' in field and field['id'] == '_id':
                    has_extra_id = True
                    json_dict['result']['fields'].remove(field)
            if has_extra_id and 'records' in json_dict['result']:
                for record in json_dict['result']['records']:
                    if '_id' in record:
                        del record['_id']
        return json.dumps(json_dict)

    def action(self, logic_function, ver=None):
        if logic_function == 'user_list' and c.pylons.request.path == '/api/action/user_list' and not c.userobj:
            return base.abort(403, u'No está autorizado para entrar a esta página')
        default_response = super(GobArApiController, self).action(logic_function, ver)
        if logic_function == 'datastore_search':
            default_response = self._remove_extra_id_field(default_response)
        return default_response

    def status(self):
        context = {'model': model, 'session': model.Session}
        data_dict = {}

        status = logic.get_action('status_show')(context, data_dict)
        gobar_status = logic.get_action('gobar_status_show')(context, data_dict)
        status['gobar_artifacts'] = gobar_status

        return self._finish_ok(status)
