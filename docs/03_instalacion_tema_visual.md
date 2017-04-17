## Instalacion
Suponiendo que la instancia de ckan está instalada en /usr/lib/ckan/default/src
```
$ . /usr/lib/ckan/default/bin/activate
(virtualenv) $ cd /usr/lib/ckan/default
(virtualenv) $ pip install -e "git+https://github.com/datosgobar/portal-andino-theme#egg=ckanext-gobar_theme"
```
Y agregar al archivo de configuracion de ckan (development.ini o production.ini) el plugin
```
ckan.plugins = (otros plugins) gobar_theme
```

## Dependencias

Instalar plugin de jerarquia para organizaciones [[link]](https://github.com/datagovuk/ckanext-hierarchy) (seguir instrucciones del repo)

## Configuracion
Dentro del archivo de configuracion de ckan (development.ini o production.ini)
```
ckan.auth.create_user_via_api = false
ckan.auth.create_user_via_web = false
ckan.locale_default = es
ckan.datasets_per_page = 8
```

La extensión necesita dos carpetas para guardar la configuración de la extensión y las imagenes que se suben para utilizar como fondo/logo/etc. Asumiendo que la extensión se instaló en `/usr/lib/ckan/default/src/ckanext-gobar-theme/`, los comandos son:
```
mkdir -p /usr/lib/ckan/default/src/ckanext-gobar-theme/ckanext/gobar_theme/public/user_images/
mkdir -p /var/lib/ckan/theme_config/
touch /var/lib/ckan/theme_config/settings.json
```
