$(function () {
    var TIME_INDEX_SPECIAL_TYPE = 'time_index';

    $('#add-col').on('click', function () {
        var newCol = $($('.resource-attributes-group')[0]).clone();
        newCol.find('input, select, textarea').val('');
        // TODO: Ocultar avanzados y especiales
        $('.resource-attributes-actions').before(newCol);
    });

    $(document).on('change', '.resource-col-special-data', function(e) {
        var parent = $(e.currentTarget).parents('.resource-attributes-group');
        var selectedSpecialType = $(e.currentTarget).val();
        var specialTypeDetail = parent.find('.resource-col-special-data-detail');
        
        specialTypeDetail.prop('disabled', selectedSpecialType != TIME_INDEX_SPECIAL_TYPE);
        specialTypeDetail.val('');
    });

    $(document).on('click', '.remove-col', function (e) {
        if (confirm("¿Seguro que desea eliminar la columna?")) {
            var colToRemove = $(e.currentTarget).parents('.resource-attributes-group');
            var isTheOnlyOne = $('.resource-attributes-group').length == 1;
            if (isTheOnlyOne) {
                colToRemove.find('input, select, textarea').val('');
                // TODO: Ocultar avanzados y especiales
            } else {
                colToRemove.remove()
            }
        }
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
                type: (attributeGroupEl.find('.resource-col-type').val() || ''),
                unit: attributeGroupEl.find('.resource-col-unit').val(),
                id: (attributeGroupEl.find('.resource-col-id').val() || ''),
                specialType: (attributeGroupEl.find('.resource-col-special-data').val() || ''),
                specialTypeDetail: (attributeGroupEl.find('.resource-col-special-data-detail').val() || ''),
            };

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
        var attributesGroups = $('.resource-attributes-group');

        var hasValue = function(thing) {
            return thing !== null && thing != '';
        }

        for (var i = 0; i < attributesGroups.length; i++) {
            var attributeGroupEl = $(attributesGroups[i]);

            // Avanzados
            var unit = attributeGroupEl.find('.resource-col-unit').val();
            var id = (attributeGroupEl.find('.resource-col-id').val() || '');

            if (hasValue(unit) || hasValue(id)) {
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
    }

    init();
});