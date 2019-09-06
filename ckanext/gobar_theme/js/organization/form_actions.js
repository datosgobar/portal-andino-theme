$(function () {
    var submit_count = 0;

    function urlValidator(errorTemplate) {
        var url = $('#field-url');
        var urlPreview = $('.slug-preview-value')
        var urlValid = true;
        if ($('.slug-preview').css('display') == 'none'){
            if (!url.val().length > 0) {
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
        var titleIsEmpty;
        var titleIsValid;
        var urlValid = true;
        var isEmptyErrorTemplate = '<div class="missing-field">Completá este dato</div>';
        var isTooLongErrorTemplate = '<div class="missing-field">El título es muy largo</div>';

        var title = $('#field-name');
        titleIsEmpty = 0 >= title.val().length;
        titleIsValid = title.val().length <= 100;

        if (titleIsEmpty){
            title.after(isEmptyErrorTemplate);
        } else if (!titleIsValid) {
            title.after(isTooLongErrorTemplate);
        } else {
            urlValid = urlValidator(isEmptyErrorTemplate);
        }

        var isValid = titleIsValid && !titleIsEmpty && urlValid;
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
