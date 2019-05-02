from pylons.controllers.util import abort

from ckanext.gobar_theme.helpers import is_plugin_present

TS_EXPLORER_PLUGIN = "seriestiempoarexplorer"


def plugin_or_404(plugin_name):
    if not is_plugin_present(plugin_name):
        abort(404, 'Plugin %s not present' % plugin_name)
