$(function () {
    var submit_count = 0;

    function urlValidator(errorTemplate) {
        var url = $('#field-url');
        var urlPreview = $('.slug-preview-value');
        var urlValid = true;
        if ($('.slug-preview').css('display') == 'none'){
            if (url.val().length < 2) {
                urlValid = false;
                url.parent().after(errorTemplate)
            }
        } else {
            if (urlPreview.text() == '<nombre-de-la-organización>') {
                urlValid = false;
                $('.slug-preview').after(errorTemplate)
            }
        }
        return urlValid;
    }

    function formIsValid() {
        $('.missing-field').remove();
        var titleIsTooShort;
        var titleIsTooLong;
        var urlValid;
        var isTooShortErrorTemplate = '<div class="missing-field">El título debe tener al menos 2 caracteres</div>';
        var isTooLongErrorTemplate = '<div class="missing-field">El título es muy largo</div>';

        var title = $('#field-name');
        titleIsTooShort = title.val().length < 2;
        titleIsTooLong = title.val().length > 100;

        if (titleIsTooShort){
            title.after(isTooShortErrorTemplate);
        } else if (titleIsTooLong) {
            title.after(isTooLongErrorTemplate);
        } else {
            urlValid = urlValidator(isTooShortErrorTemplate);
        }

        var isValid = !titleIsTooLong && !titleIsTooShort && urlValid;
        if (!isValid) {
            window.scrollTo(0, 0);
        }

        return isValid;
    }

    $(document).on('click', '.btn-mini', function () {
        if (submit_count > 0){
            return formIsValid();
        }
    });

    $('form#organization-edit-form').submit(function () {
        submit_count++;
        return formIsValid();
    });

});
