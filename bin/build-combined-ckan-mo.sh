msgcat --use-first \
    "/usr/lib/ckan/default/src/ckanext-gobar-theme/ckanext/gobar_theme/i18n/es/LC_MESSAGES/ckan.po" \
    "/usr/lib/ckan/default/src/ckan/ckan/i18n/es/LC_MESSAGES/ckan.po" \
| msgfmt - -o "/usr/lib/ckan/default/src/ckan/ckan/i18n/es/LC_MESSAGES/ckan.mo"
