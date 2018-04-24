#! coding: utf-8

from ckan.lib.base import BaseController
import ckan.lib.base as base
import ckanext.gobar_theme.lib.datajson_actions as datajson_actions


class GobArDatajsonController(BaseController):

    def datajson(self):
        return base.render('datajson.html', extra_vars={'datajson': datajson_actions.read_or_generate_datajson()})
