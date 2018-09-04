# coding=utf-8
from ckanext.gobar_theme.lib.datajson_actions import get_data_json_contents, CACHE_FILENAME
from ckanapi import RemoteCKAN, LocalCKAN
from ckan import model
from pylons.config import config
from pydatajson import DataJson
import subprocess
import ckanext

# Busco los ids de los recursos que existen en el datajson
# TODO: usar la api de pydatajson
datajson_resource_ids = []
# datajson_contents = get_data_json_contents()
# for dataset in datajson_contents.get('dataset', None):
#     for resource in datajson_contents.get('distribution', None):
#         datajson_resource_ids.append(resource.get('identifier'))
catalog = DataJson(CACHE_FILENAME)
for resource in catalog.distributions:
    datajson_resource_ids.append(resource.get('identifier'))

# Busco los recursos que actualmente se encuentran en el DataStore
# TODO: Preguntar a Lucas R si se puede hacer usando algún cliente python de CKAN
#ckan_cli.datastore_search()
site_url = config.get('ckan.site_url')
if not site_url.startswith('http'):
    site_url = 'http://' + site_url

lc = LocalCKAN(username='default')
apikey = lc._get_action('get_site_user')({'ignore_auth': True}, ()).get('apikey')
demo = RemoteCKAN(site_url, apikey)
context = {'model': model, 'session': model.Session, 'user': lc._get_action('get_site_user')({'ignore_auth': True}, ())}
current_offset = 0
r = demo.action.datastore_search(resource_id='_table_metadata')
while r.get('total') > current_offset:
    for datastore_resource in r.get('records'):
        datastore_resource_id = datastore_resource.get('name')
        if datastore_resource_id != "_table_metadata" and datastore_resource_id not in datajson_resource_ids:
            # ckanext.datastore.logic.action.datastore_delete(context, {'resource_id': datastore_resource_id, 'force': True})
            # subprocess.check_call([
            #     "curl",
            #     "-X",
            #     "POST",
            #     site_url + "/api/3/action/datastore_delete",
            #     "-H",
            #     "\"Authorization:",
            #     apikey + "\"",
            #     "-d",
            #     "'{\"force\":\"True\",",
            #     "\"resource_id\":",
            #     datastore_resource_id + "\"}'"
            # ])
            demo.action.datastore_delete(resource_id=datastore_resource_id, force=True)
            # borrar recurso del datastore
    current_offset += 100
    r = demo.action.datastore_search(resource_id='_table_metadata', offset=current_offset)




# demo = RemoteCKAN('https://demo.ckan.org', user_agent=ua)
# r = demo.action.datastore_search(resource_id='_table_metadata', offset=100)
# Ver el offset: ir haciendo de a 100 hasta que el len del resultado de 0


# # Consigo todos los recursos del DataStore que no están en el datajson
# datastore_resource_ids_to_delete = []
# for record in result.get('records'):
#     datastore_resource_id = record.get('name')
#     if datastore_resource_id != "_table_metadata" and datastore_resource_id not in datajson_resource_ids:
#         datastore_resource_ids_to_delete.append(datastore_resource_id)

# KILL 'EM ALL
# for resource_id in datastore_resource_ids_to_delete:
#     pass
#     # TODO: Ver si se puede usar un cliente de python de la API de CKAN
#     # curl -X POST "http://demo.ckan.org/api/3/action/datastore_delete" -d
#     # '{"filters":{"_id":[1,2]},"force":"true","resource_id":"a43bfb04-7a8b-4624-a06a-25f4165e5b2a"}'
#     # -H "Authorization: xxx"
# (nota: cambiar url para que use `site_url`)

# ===========================================================

# Extra (para cuando se instala Andino)
# from pylons.config import config
# cron_schedule = config.get('ckan.datastore_purge_schedule')
