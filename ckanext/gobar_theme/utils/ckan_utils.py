import pylons.config as config
from pylons.controllers.util import abort


TS_EXPLORER_PLUGIN = "seriestiempoarexplorer"

def is_plugin_present(plugin_name):
    plugins = config.get('ckan.plugins')
    return plugin_name in plugins


def plugin_or_404(plugin_name):
    if not is_plugin_present(plugin_name):
        abort(404, 'Plugin %s not present' % plugin_name)
