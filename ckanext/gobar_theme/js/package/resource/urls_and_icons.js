$(function () {

    var file_or_url_was_removed = false;

    $(document).on('click', '.url-button', function (e) {
        if($(this).siblings("#resource-upload-url").length > 0) {  // Aseguro que se esté clickeando el botón de URL
            if ($('#distribution-type').val() !== 'api'){
                $('#form-file-name').show();
                $('#field-file-name').show();
            }
            $('option.distribution-type-option[value="file.upload"]').val('file');
        }
    });

    $(document).on('click', '.file-upload-label', function (e) {
        $('input#' + $(e.target).parent().attr('for')).click();  // Disparo el click en el input[type=file]
        $('option.distribution-type-option[value="file"]').val('file.upload');
    });

    $(document).on('click', 'a.btn-remove-url', function (e) {
        if ($(this).siblings("input#resource-upload-url").length > 0) {  // Aseguro que se esté cerrando el input de URL
            $('#form-file-name').hide();
            $('input#field-file-name').val('');
            file_or_url_was_removed = true;
        }
    });

    $('form#resource-edit').on('submit', function (e) {
        if (file_or_url_was_removed === false){
            $('input[name=clear_upload]').remove()
        }
    });

});