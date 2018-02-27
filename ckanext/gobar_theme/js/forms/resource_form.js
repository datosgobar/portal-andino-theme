$(function () {
    var TIME_INDEX_SPECIAL_TYPE = 'time_index';

    var resetColumnHeadersCounter = function() {
        $('.resource-attributes-header > div').each(function(index) {
            $( this ).text('Columna ' + (index + 1));
            $($( this ).siblings()[0]).attr('data-index', index);  // Add calculated id as data-index to use to delete the column
        });
    }

    var resetAdvancedAndSpecialButtonsAndInputs = function(parent) {
        parent.find('.add-extra-fields-advanced').show();
        parent.find('.resource-col-advanced-container').hide();
        parent.find('.add-extra-fields-special').show();
        parent.find('.resource-col-special-data-container').hide();
    }

    $('#add-col').on('click', function () {
        var newCol = $($('.resource-attributes-group')[0]).clone();
        newCol.find('input, select, textarea').val('');
        resetAdvancedAndSpecialButtonsAndInputs(newCol);

        $('.resource-attributes-actions').before(newCol);

        resetColumnHeadersCounter();
    });

    $(document).on('change', '.resource-col-special-data', function(e) {
        var parent = $(e.currentTarget).parents('.resource-attributes-group');
        var selectedSpecialType = $(e.currentTarget).val();
        var specialTypeDetail = parent.find('.resource-col-special-data-detail');
        
        specialTypeDetail.prop('disabled', selectedSpecialType != TIME_INDEX_SPECIAL_TYPE);
        specialTypeDetail.val('');
    });

    $(document).on('click', '#delete-col-btn', function(e) {
        var columnIdToRemove = $(e.currentTarget).data('col-to-delete');  // Get the index of the col to remove
        var colToRemove = $('i.col-options[data-index="' + columnIdToRemove + '"]').parents('.resource-attributes-group');
        var isTheOnlyOne = $('.resource-attributes-group').length == 1;
        if (isTheOnlyOne) {
            colToRemove.find('input, select, textarea').val('');  // Elimina los datos de la sección de la columna, pero deja la sección
            resetAdvancedAndSpecialButtonsAndInputs(colToRemove);
        } else {
            colToRemove.remove()
        }
        resetColumnHeadersCounter();
    });

    $(document).on('click', '.add-extra-fields-advanced', function (e) {
        var $target = $(e.currentTarget);
        var $parent = $target.parents('.resource-attributes-group');

        $parent.find('.add-extra-fields-advanced').hide();
        $parent.find('.resource-col-advanced-container').show();
    });

    $(document).on('click', '.add-extra-fields-special', function (e) {
        var $target = $(e.currentTarget);
        var $parent = $target.parents('.resource-attributes-group');

        $parent.find('.add-extra-fields-special').hide();
        $parent.find('.resource-col-special-data-container').show();
    });

    function addAttributesHidden() {
        var attributesGroups = $('.resource-attributes-group');
        var attributes = [];
        for (var i = 0; i < attributesGroups.length; i++) {
            var attributeGroupEl = $(attributesGroups[i]);
            var attributeGroup = {
                title: attributeGroupEl.find('.resource-col-name').val(),
                description: attributeGroupEl.find('.resource-col-description').val(),
                type: (attributeGroupEl.find('.resource-col-type').val() || '')
            };

            var updateAttributesIfValueExist = function(attributeGroup, attributeName, selector) {
                var value = (attributeGroupEl.find(selector).val() || '');
                if (value != null && value != '') {
                    attributeGroup[attributeName] = value;
                }
            }

            updateAttributesIfValueExist(attributeGroup, 'units', '.resource-col-units');
            updateAttributesIfValueExist(attributeGroup, 'id', '.resource-col-id');
            updateAttributesIfValueExist(attributeGroup, 'specialType', '.resource-col-special-data');
            updateAttributesIfValueExist(attributeGroup, 'specialTypeDetail', '.resource-col-special-data-detail');

            if (attributeGroup.title.length > 0 || attributeGroup.type.length > 0 || attributeGroup.description.length > 0) {
                attributes.push(attributeGroup);
            }
        }
        $('#attributes-description').val(JSON.stringify(attributes));
    }

    $('form#resource-edit').on('submit', function (e) {
        addAttributesHidden();
        return true
    });

    var init = function() {
        // Inicializa el formulario (los medatatos de campo)
        resetColumnHeadersCounter();

        var attributesGroups = $('.resource-attributes-group');

        var hasValue = function(thing) {
            return thing !== null && thing != '';
        }

        for (var i = 0; i < attributesGroups.length; i++) {
            var attributeGroupEl = $(attributesGroups[i]);

            // Avanzados
            var units = attributeGroupEl.find('.resource-col-units').val();
            var id = (attributeGroupEl.find('.resource-col-id').val() || '');

            if (hasValue(units) || hasValue(id)) {
                // Muestro el form y oculto el botón
                attributeGroupEl.find('.add-extra-fields-advanced').hide();
                attributeGroupEl.find('.resource-col-advanced-container').show();
            }

            // Especiales
            var specialType = (attributeGroupEl.find('.resource-col-special-data').val() || '');
            var specialTypeDetail = (attributeGroupEl.find('.resource-col-special-data-detail').val() || '');

            if (hasValue(specialType) || hasValue(specialTypeDetail)) {
                // Muestro el form y oculto el botón
                attributeGroupEl.find('.add-extra-fields-special').hide();
                attributeGroupEl.find('.resource-col-special-data-container').show();
            }
        }

        $(document).on('click', '#btn-save-col-sort', function(e) {
            var newOrders = $("ul.sort-col-list").sortable('serialize').get()[0];

            for (var i = 0; i < newOrders.length; i++) {
                var newOrder = newOrders[i];
                // Al quitar del dom y agregarlos de nuevo al final según el orden especificado
                // en "New Order" dejo los campos ordenados como corresponde.
                var colunmDefinition = $('i.col-options[data-index=' + newOrder.index + ']').parents('.resource-attributes-group').detach();
                colunmDefinition.appendTo('.resource-attributes-group-container');
            }

            resetColumnHeadersCounter();
        });

        var menu = new BootstrapMenu('.col-options', {
            menuEvent: 'click',
            fetchElementData: function($elem) {
                return $elem.data('index');
            },
            actions: {
                sortColumns: {
                    name: 'Reordenar columnas',
                    onClick: function() {
                        // Genero los elementos del DOM que representan las columnas ordenables
                        // Template: <li data-index="0"><i class="icon-ellipsis-vertical"></i>Columna 1</li>
                        var generateSortableElement = function(index, text) {
                            text = text || "Columna " + (index + 1);  // Defaulteo el texto a mostrar si no me mandaron nada
                            var div = document.createElement('div');
                            div.innerHTML = '<li data-index="' + index + '"><i class="icon-ellipsis-vertical"></i>' + text + '</li>';

                            return div.firstChild;
                        }

                        var sortableElementsContainer = $('ul.sort-col-list');
                        sortableElementsContainer.empty();
                        var attributesGroups = $('.resource-attributes-group');
                        for (var i = 0; i < attributesGroups.length; i++) {
                            var attributeGroupEl = $(attributesGroups[i]);
                            
                            var text = attributeGroupEl.find('.resource-col-name').val();
                            var index = attributeGroupEl.find('.resource-attributes-header > i').data('index');

                            // Genero y agrego un elemento al contenedor
                            sortableElementsContainer.append(generateSortableElement(index, text));
                        }

                        var columns = $("ul.sort-col-list").sortable({
                            group: 'sort-col-list'
                        });
                        $('#sort-col-modal').modal();
                    }
                },
                removeColumn: {
                    name: 'Eliminar columna',
                    classNames: 'remove-column-menu-option',
                    onClick: function(columnId) {
                        $('#delete-col-btn').data('col-to-delete', columnId);  // Propagate the column ID as data of the delete button of the modal
                        $('#delete-col-modal').modal();
                    }
                }
            }   
        });
    }

    init();
});