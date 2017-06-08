function validLength(length, maxLength) {
    return maxLength >= length;
}

function validTitle(){
    var titleLength = $('input[data-valid-title-length]').val().length;
    var validTitleLength = $('div[data-valid-title-length]').data('valid-title-length')
    return validLength(titleLength, validTitleLength);
}

function validDesc(){
    var descLength = $('textarea[data-valid-desc-length]').val().length
    var validDescLength = $('textarea[data-valid-desc-length]').data('valid-desc-length')
    return validLength(descLength, validDescLength);
}

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

        isFormValid = isValid && validTitle() && validDesc();

        if (!isFormValid) {
            window.scrollTo(0, 0);
        }
        
        return isFormValid;
    }

    $('form#resource-edit').submit(function () {
        return formIsValid();
    });

    $(document).ready(function(){
        var validTitleLength = $('div[data-valid-title-length]').data('valid-title-length')
        var validDescLength = $('textarea[data-valid-desc-length]').data('valid-desc-length')

        if (!validTitle()){
            $('div#field-name.after-desc').addClass('long-field')
        }

        if (!validDesc()){
            $('div#field-description.after-desc').addClass('long-field')
        }
    });
});
