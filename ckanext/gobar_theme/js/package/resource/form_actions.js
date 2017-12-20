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

function validateTitle() {
    $('div#field-name.after-desc').toggleClass('long-field', !validTitle())
}

function validateDesc() {
    $('div#field-description.after-desc').toggleClass('long-field', !validDesc())
}

$(function () {
    var clickCount = 0;
    var clickedPublishButton = false;
    var titleValid = false;
    var hasResources = Number($('form#resource-edit').data('resources-amount')) > 0;

    function errorMessages() {
        var isValid = true;
        var title = $('#field-name');
        var errorTemplate = '<div class="missing-field">Completá este dato</div>';
        titleValid = title.val().length > 0;

        if (!titleValid) {
            isValid = false;
            title.after(errorTemplate);
            window.scrollTo(0, 0);
        }
        return isValid;
    }

    function formIsValid() {
        $('.missing-field').remove();

        if (clickCount > 0) {
            var canPublish = false;
            if (clickedPublishButton) {
               if (hasResources) {
                    canPublish = true;
               } else {
                    canPublish = errorMessages();
               }

               if (!canPublish) {
                    window.scrollTo(0, 0);
                    return canPublish;
                }
            } else {
                return errorMessages();
            }
        }

        return true;

        var isValid = true;
        var errorTemplate = '<div class="missing-field">Completá este dato</div>';

        if (clickCount > 0) {
            var title = $('#field-name');
            if (title.val().length == 0){
                isValid = false;
                title.after(errorTemplate)
            }

            isFormValid = isValid && validTitle() && validDesc();

            if (!isFormValid) {
                window.scrollTo(0, 0);
            }
        }

        return isFormValid;
    }

    $('form#resource-edit').submit(function () {
        return formIsValid();
    });

    $('button#again-button').on('click', function(){
        clickCount++;
    });

    $('button#draft-button').on('click', function(){
        clickCount++;
    });

    $('button#publish-button').on('click', function(){
        clickCount++;
        clickedPublishButton = true;
    });

    $(document).ready(function(){
        validateTitle()
        $('input[data-valid-title-length]').on('change input keyup', validateTitle)

        validateDesc()
        $('textarea[data-valid-desc-length]').on('change input keyup', validateDesc)
    });
});
