$(function() {

    $('form:has(input.url-field[type=text]), form:has(div.url-field > div > input[type=text])').on('submit', function(event) {

        var URL_VALIDATION_REGEX = new RegExp(
            /^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-.]{1}[a-z0-9]+)*(\.[a-z0-9]{2,5}|(:[0-9]{1,5}))(\/.*)?$/
        );

        var HEADER_HEIGHT = $('#header').height();

        $(event.target).find('input.url-field[type=text], div.url-field > div > input[type=text]').each(function(index) {
            if ( !$('input').is('[readonly]') ){
                // Si la validación falla, abortar el submit y mostrar un mensaje de validación
                var that = $(this);
                if (that.val() && !that.val().match(URL_VALIDATION_REGEX)) {
                    // Agrego el mensaje de error

                    if (!that.data('validation-failed')) {
                        var errorMessageTemplate = '<label for="' + (that.attr('id') || '') + '" class="form-error-message">La url ingresada no es válida</label>';
                        that.after(errorMessageTemplate);
                        $('html, body').animate({
                            scrollTop: (that.first().offset().top - HEADER_HEIGHT)
                        }, 500);

                        that.data('validation-failed', true);
                    }

                    event.preventDefault();  // Evitamos que el form haga el submit
                } else {
                    that.data('validation-failed', false);
                }
            }
        });
    });
});
