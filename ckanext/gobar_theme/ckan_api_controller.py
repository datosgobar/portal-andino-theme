# coding=utf-8

import json
import random
import string

from webob.exc import HTTPNotFound
import ckan.lib.activity_streams as activity_streams
import ckan.lib.base as base
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.helpers as h
import ckan.lib.mailer as ckan_mailer
import ckan.lib.search as search
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as p
from ckan.common import request, c, _, response
from ckan.controllers.api import ApiController

import ckanext.gobar_theme.mailer as mailer
from ckan.lib.base import abort
import ckan.lib.jsonp as jsonp

parse_params = logic.parse_params
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized


class GobArCkanUserController(ApiController):
    json_content_type = 'application/json;charset=utf-8'

    @jsonp.jsonpify
    def user_autocomplete(self):
        return ["No estás autorizado para ver esta página"]
        base.abort(403, _('Not authorized to see this page'))
