from ckanext.gobar_theme.utils.andino_version import get_portal_andino_version


def portal_andino_version():
    version = get_portal_andino_version() or 'Desarrollo'

    version = version.replace('release-', '')  # Elimino el release-
    version = version[:15]  # me quedo con los primeros 15 caracteres

    return version
