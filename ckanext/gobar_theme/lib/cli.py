from ckan.lib import cli
from ckanext.gobar_theme.lib.datajson_actions import update_datajson_cache, update_catalog
import logging
import ckan.logic.schema.job_clear_schema
import ckan.logic.action.delete


class GenerateDataJsonCommand(cli.CkanCommand):

    summary = "Generar el data.json al instalar o actualizar andino"

    def command(self):
        logging.info("Generando el data.json")
        try:
            update_datajson_cache()
        except Exception:
            logging.error("Error generando el data.json")


class GenerateCatalogXlsxCommand(cli.CkanCommand):

    summary = "Generar el catalog.xlsx al instalar o actualizar andino"

    def command(self):
        logging.info("Generando el catalog.xlsx")
        try:
            update_catalog()
        except Exception:
            logging.error("Error generando el catalog.xlsx")
