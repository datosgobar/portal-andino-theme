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

});
