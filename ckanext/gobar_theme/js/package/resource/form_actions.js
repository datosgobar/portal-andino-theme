$(function () {
    var clickCount = 0;
    function formIsValid() {
        $('.missing-field').remove();
        var titleValid = true;
        var errorTemplate = '<div class="missing-field">Completá este dato</div>';

        if (clickCount > 0) {
            var title = $('#field-name');
            titleValid = title.val().length > 0;

            if (!titleValid) {
                title.after(errorTemplate);
                window.scrollTo(0, 0);
            }
        }

        return titleValid;
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
    });

});
