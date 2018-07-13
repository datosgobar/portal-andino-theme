from ckan.lib import cli
from ckanext.gobar_theme.lib.datajson_actions import update_catalog, update_datajson_cache
import logging


class GenerateDataJsonCommand(cli.CkanCommand):

    summary = "Generar el data.json al instalar o actualizar andino"

    def command(self):
        logging.info("Generando el data.json")
        self._load_config()
        try:
            update_datajson_cache()
        except Exception as e:
            logging.exception("Error generando el data.json: %s", e)


class GenerateCatalogXlsxCommand(cli.CkanCommand):

    summary = "Generar el catalog.xlsx al instalar o actualizar andino"

    def command(self):
        logging.info("Generando el catalog.xlsx")
        self._load_config()
        try:
            update_catalog()
        except Exception as e:
            logging.exception("Error generando el catalog.xlsx: %s", e)
