# portal-andino-theme

Repositorio de la extensión del Portal Andino de la República Argentina para [CKAN](http://ckan.org/). Este proyecto se encarga de modificaciones al ruteo de la aplicación web, cambios visuales a la interfaz, customización del portal, analytics y gestión de usuarios, permisos y roles, entre otros. Este repositorio *no* constituye el proyecto entero. El repositorio central del proyecto del Portal Andino es [portal-andino](https://github.com/datosgobar/portal-andino)

- [Instalación](#instalaci%C3%B3n)
- [Desarrollo](#desarrollo)
- [Uso del theme](#uso-del-theme)
- [Créditos](#cr%C3%A9ditos)
- [Consultas sobre Andino](#consultas-sobre-andino)
- [Contacto](#contacto)

## Instalación

La instalación del paquete completo está disponible como un contenedor de Docker. Seguir las instrucciones del repositorio del [Portal Andino](https://github.com/datosgobar/portal-andino) para levantar la instancia con Docker.

## Desarrollo

Como alternativa a la instalación dockerizada existe la posibilidad de tener una instalación contenida en un `virtualenv` del sistema. Esto se puede obtener siguiendo las instrucciones de [esta guia](http://docs.ckan.org/en/ckan-2.5.2/maintaining/installing/install-from-source.html). Una vez instalado el paquete a nivel sistema, es posible linkear el proceso principal a un debbuger de python (por ej pycharm). Este metodo no es recomendado para hacer modificaciones que impacten en el manejo del servidor por parte del wsgi de apache o nginx. Para dicho caso, es necesario tener una instalación de la aplicación dockerizada y acceder al contenedor del theme para realizar el desarrollo necesario.

Esta extensión de ckan fue desarrollada siguiendo la [guia de creación de extensiones](http://docs.ckan.org/en/ckan-2.5.2/extensions/tutorial.html).

## Uso del theme

Está disponible una [guía de uso](./docs/guia_uso_portal_andino.md) dentro de la documentación de este repositorio.

## Créditos

Este repositorio es un fork de la extensión de CKAN de [datos.gob.ar](https://github.com/datosgobar/datos.gob.ar)

## Consultas sobre Andino

**Andino es un portal abierto en constante desarrollo** para ser usado por toda la comunidad de datos. Por eso, cuando incorporamos una nueva mejora, **cuidamos mucho su compatibilidad con la versión anterior**.

Como la comunidad de datos es grande, **por ahora no podemos dar soporte técnico frente a modificaciones particulares del código**. Sin embargo, **podés contactarnos para despejar dudas**.

## Contacto

Te invitamos a [crearnos un issue](https://github.com/datosgobar/portal-andino-theme/issues/new?title=Encontre%20un%20bug%20en%20andino) en caso de que encuentres algún bug o tengas feedback de alguna parte de `portal-andino-theme`.

Para todo lo demás, podés mandarnos tu comentario o consulta a [datos@modernizacion.gob.ar](mailto:datos@modernizacion.gob.ar).
