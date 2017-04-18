$(function () {
    var submit_count = 0;
    function formIsValid() {
        $('.missing-field').remove();
        var isValid = true;
        var errorTemplate = '<div class="missing-field">Completá este dato</div>';

        var title = $('#field-name');
        if (!title.val().length > 0) {
            isValid = false;
            title.after(errorTemplate)
        }

        var url = $('#field-url');
        var url_preview = $('.slug-preview-value')
        if ($('.slug-preview').css('display') == 'none'){
            if (!url.val().length > 0) {
                isValid = false;
                url.parent().after(errorTemplate)
            }
        } else {
            if (url_preview.text() == '<nombre-del-grupo>') {
                isValid = false;
                $('.slug-preview').after(errorTemplate)
            }
        }

        if (!isValid) {
            window.scrollTo(0, 0);
        }

        return isValid;
    };

    $(document).on('click', '.btn-mini', function () {
        if (submit_count > 0){
            return formIsValid();
        }
    });

    $('form#group-edit').submit(function () {
        submit_count++;
        return formIsValid();
    });

});
