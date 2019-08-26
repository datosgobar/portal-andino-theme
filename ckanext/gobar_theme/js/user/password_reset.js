$(function () {
    $('#password-reset').modal('show');

    var validatePassword = function () {
        var input1 = $('#password1');
        var input2 = $('#password2');
        clearFeedback(input1);
        clearFeedback(input2);
        if (input1.val().length == 0) {
            showNegativeFeedback(input1, 'Completá este dato.')
            return false
        }
        if (input2.val().length == 0) {
            showNegativeFeedback(input2, 'Completá este dato.')
            return false
        }
        if (input1.val() != input2.val()) {
            showNegativeFeedback(input2, '¡Oh! Las contraseñas no coinciden. Probá otra vez.');
            return false
        }

        if (!securePassword(input2.val())) {
            insecurePasswordMessage(input2);
            return false;
        }
        return true
    };

    var validateEmail = function () {
        var input1 = $('#email1');
        var input2 = $('#email2');
        clearFeedback(input1);
        clearFeedback(input2);
        var val1 = input1.val().trim();
        var val2 = input2.val().trim();
        if (val1.length > 0 && val2.length == 0) {
            showNegativeFeedback(input2, 'Completá este dato.')
            return false;
        }
        if (val2.length > 0 && val1.length == 0) {
            showNegativeFeedback(input1, 'Completá este dato.')
            return false;
        }
        if (val1.length > 0) {
            if (!email_re.test(val1)) {
                showNegativeFeedback(input1, 'Usá este formato nombre@ejemplo.com.');
                return false;
            }
            if (!email_re.test(val2)) {
                showNegativeFeedback(input2, 'Usá este formato nombre@ejemplo.com.');
                return false;
            }
        }
        if (val1 != val2) {
            showNegativeFeedback(input2, '¡Oh! Los e-mails no coinciden. Probá otra vez.');
            return false
        }
        return true
    };

    var sendData = function () {
        var password = $('#password1').val().trim();
        var data = {
            password: password,
            key: $('#password-reset').data('key'),
            token: $("#token-generator input").val()
        }
        var email = $('#email1').val().trim();
        if (email.length > 0) {
            data.email = email
        }
        var url = '';
        var callback = function (response) {
            if (response.success) {
                window.location.href = response.redirect_url;
            }
        };
        var failCallback = function () {
            showNegativeFeedback("Error en la validación del servidor. Intente pedir un reinicio de contraseña nuevamente, y siguiendo el nuevo link del mail")
        };
        $.post(url, data, callback).fail(failCallback);
    };

    $('#save-changes').on('click', function () {
        var passwordValid = validatePassword();
        var emailValid = validateEmail();
        if (passwordValid && emailValid) {
            sendData();
        };
    })
});