$(function () {
    function formIsValid() {
        $('.missing-field').remove();
        var isValid = true;
        var errorTemplate = '<div class="missing-field">Completá este dato</div>';

        var title = $('#field-name');
        if (title.val().length == 0){
            isValid = false;
            title.after(errorTemplate)
        }

        if (!isValid) {
            window.scrollTo(0, 0);
        }
        return isValid;
    }

    $('form#resource-edit').submit(function () {
        return formIsValid();
    });

    $(document).ready(function(){
        var validTitleLength = $('div[data-valid-title-length]').data('valid-title-length')
        var validDescLength = $('div[data-valid-desc-length]').data('valid-desc-length')


        if (validTitleLength != "True"){
            $('div#field-name.after-desc').addClass('missing-field')
        }

        if (validTitleLength != "True"){
            $('div#field-description.after-desc').addClass('missing-field')
        }
    });
});
