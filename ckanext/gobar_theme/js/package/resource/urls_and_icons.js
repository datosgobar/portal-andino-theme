$(function () {

    $(document).on('click', '.url-button', function () {
        if ($('#distribution-type').val() !== 'api'){
            $('#form-file-name').show();
        }
        $('option.distribution-type-option[value="file.upload"]').val('file');
    });

    $(document).on('click', '.file-upload-label', function () {
        $('input#' + $(event.target).parent().attr('for')).click();  // Disparo el click en el input[type=file]
        $('#form-file-name').hide();
        $('option.distribution-type-option[value="file"]').val('file.upload');
    });

});