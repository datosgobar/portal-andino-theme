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
        var callback = function (response) {
            if (!response.success && response.error == 'not_found') {
                showNegativeFeedback(userInput, '¡Oh! No encontramos este usuario. Probá con otro.')
            } else if (!response.success) {
                showNegativeFeedback(userInput, '') // TODO: mensaje de error inesperado
            } else {
                showPositiveFeedback(userInput, '¡Perfecto! Te enviamos un e-mail para que crear una nueva contraseña.')
            }
        };
        var failCallback = function () {
            var feedback = '¡Oh! No encontramos este usuario. Probá con otro.'
        };
        $.post('/olvide_mi_contraseña', {user: username}, callback).fail(failCallback);
    })
});