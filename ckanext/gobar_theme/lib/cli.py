#! coding: utf-8
from ckan.lib import cli
from ckanext.gobar_theme.lib.datajson_actions import CACHE_FILENAME
from ckanapi import RemoteCKAN, LocalCKAN
from pylons.config import config
from pydatajson import DataJson

import logging

LOGGER = logging.getLogger("ckan")


class GenerateDataJsonCommand(cli.CkanCommand):
    summary = "Generar el data.json al instalar o actualizar andino"

    def command(self):
        self._load_config()
        # Importamos luego de `_load_config` para evitar un error en runtime debido a que CKAN no fue inicializado.
        from ckanext.gobar_theme.lib.datajson_actions import update_datajson_cache

        LOGGER.info("Generando el data.json")

        try:
            update_datajson_cache()
        except Exception as e:
            LOGGER.exception("Error generando el data.json: %s", e)


class GenerateCatalogXlsxCommand(cli.CkanCommand):
    summary = "Generar el catalog.xlsx al instalar o actualizar andino"

    def command(self):
        self._load_config()
        # Importamos luego de `_load_config` para evitar un error en runtime debido a que CKAN no fue inicializado.
        from ckanext.gobar_theme.lib.datajson_actions import update_catalog

        LOGGER.info("Generando el catalog.xlsx")

        try:
            update_catalog()
        except Exception as e:
            LOGGER.exception("Error generando el catalog.xlsx: %s", e)


class UpdateDatastoreCommand(cli.CkanCommand):
    summary = ""

    def command(self):
        self._load_config()

        LOGGER.info("Updating datastore")

        # Acumulo todos los ids de los recursos del nodo
        datajson_resource_ids = []
        catalog = DataJson(CACHE_FILENAME)
        for resource in catalog.distributions:
            datajson_resource_ids.append(resource.get('identifier'))

        # Usando un LocalCKAN obtendo el apikey del usuario default
        lc = LocalCKAN()
        apikey = lc._get_action('get_site_user')({'ignore_auth': True}, ()).get('apikey')

        # La búsqueda de recursos en Datastore falla si la url no comienza con 'http'
        site_url = config.get('ckan.site_url')
        if not site_url.startswith('http'):
            site_url = 'http://' + site_url

        # Obtengo informacion de los elementos del datastore
        rc = RemoteCKAN(site_url, apikey)
        datastore_resources = rc.action.datastore_search(resource_id='_table_metadata')

        # Se borrarán los recursos del Datastore que no figuren en `datajson_resource_ids`
        # La función `datastore_search` muestra 100 resultados, por lo que es necesario utilizar un offset
        current_offset = 0
        while datastore_resources.get('total') > current_offset:
            for datastore_resource in datastore_resources.get('records'):
                # En Datastore, el id del recurso se busca como `name` (y buscamos los que no sean "_table_metadata")
                datastore_resource_id = datastore_resource.get('name')
                if datastore_resource_id != "_table_metadata" and datastore_resource_id not in datajson_resource_ids:
                      rc.action.datastore_delete(resource_id=datastore_resource_id, force=True)
            current_offset += 100
            datastore_resources = rc.action.datastore_search(resource_id='_table_metadata', offset=current_offset)

        LOGGER.info("Finished updating datastore")
