$(function () {
    var maxTitleCharacters = 150;
    var maxDescCharacters = 200;

    function lengthErrorTemplate(amountOfCharacters){
        return '<div class="missing-field">Este campo no debe superar los ' + amountOfCharacters +' caracteres</div>';
    }

    function formIsValid() {
        $('.missing-field').remove();
        var isValid = true;

        var title = $('#field-name');
        if (title.val().length > maxTitleCharacters){
            isValid = false;
            title.after(lengthErrorTemplate(maxTitleCharacters))
        }

        var description = $('#field-description');
        if (description.val().length > maxDescCharacters){
            isValid = false;
            description.after(lengthErrorTemplate(maxDescCharacters))
        }

        return isValid;
    }

    $('form#resource-edit').submit(function () {
        return formIsValid();
    });

});