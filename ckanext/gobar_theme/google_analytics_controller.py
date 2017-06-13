import ckanext.googleanalytics.plugin as google_analytics
from ckan.lib.base import BaseController, c


class GobArGAController(BaseController):
    def resource_view_embed(self, resource_id):
        google_analytics._post_analytics(c.user, 'CKAN Resource Embed', 'Resource ', resource_id, resource_id)
