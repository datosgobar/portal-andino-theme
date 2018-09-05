$(function () {

    $(document).on('click', '.url-button', function () {
        if($(this).siblings("#resource-upload-url").length > 0) {  // Aseguro que se esté clickeando el botón de URL
            if ($('#distribution-type').val() !== 'api'){
                $('#form-file-name').show();
                $('#field-file-name').show();
            }
            $('option.distribution-type-option[value="file.upload"]').val('file');
        }
    });

    $(document).on('click', '.file-upload-label', function () {
        $('input#' + $(event.target).parent().attr('for')).click();  // Disparo el click en el input[type=file]
        $('#form-file-name').hide();
        $('option.distribution-type-option[value="file"]').val('file.upload');
    });

});