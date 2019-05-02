#!coding=utf-8
from ckan import model as model


def license_options(_existing_license_id=None):
    # En lugar de retornar una lista de tuplas, como hace el código original de CKAN, retorno una lista de licencias
    # para soportar el uso del campo 'license_ids'
    register = model.Package.get_license_register()
    sorted_licenses = sorted(register.values(), key=lambda x: x.title)
    return sorted_licenses


def id_belongs_to_license(_id, _license):
    return _id == _license.id or (hasattr(_license, 'legacy_ids') and _id in _license.legacy_ids)


def get_license(_id):
    for _license in license_options():
        if id_belongs_to_license(_id, _license):
            return _license
    return None


def get_license_title(license_id):
    for _license in license_options():
        if id_belongs_to_license(license_id, _license):
            return _license.title
    return None