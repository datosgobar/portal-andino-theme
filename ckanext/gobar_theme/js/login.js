$(function () {
    $('#password-reset-show-modal').click(function () {
        $('.modal').modal('show')
    });
    $('#send-recovery').on('click', function () {
        var userInput = $('#username');
        clearFeedback(userInput);
        var username = userInput.val().trim();
        if (!username || username.length == 0) {
            showNegativeFeedback(userInput, 'Completá este dato.')
            return
        }
        var button = $('#send-recovery');
        button.prop('disabled', true);
        var callback = function (response) {
            if (!response.success && response.error == 'not_found') {
                button.prop('disabled', false);
                showNegativeFeedback(userInput, '¡Oh! No encontramos este usuario. Probá con otro.')
            } else if (!response.success) {
                button.prop('disabled', false);
                if (response.error.indexOf('Connection refused') != -1) {
                    showNegativeFeedback(userInput, 'Hemos tenido un error al intentar enviarte un email. Contactate con tu administrador')
                } else {
                    showNegativeFeedback(userInput, '') // TODO: mensaje de error inesperado
                }
            } else {
                window.location.href = "/ingresar?email-feedback=true"
            }
        };
        var failCallback = function () {
            var feedback = '¡Oh! No encontramos este usuario. Probá con otro.'
        };
        $.post('/olvide_mi_contraseña', {user: username}, callback).fail(failCallback);
    })
});