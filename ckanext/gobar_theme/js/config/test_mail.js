$(function () {
    $('#send-test-mail').on('click', function () {
        var button = $(this);
        var csrf_input = $("#login-vertical-wrapper").find("form").children("input")[0];
        var data = {};
        if (csrf_input !== undefined) {
            data['token'] = csrf_input.value;
        }
        showPositiveFeedback(button, 'Enviando mail...');
        $.post('/configurar/mail_de_prueba', data, function(){})
            .fail(
                function(jqXHR) {
                    console.log(jqXHR);
                    showNegativeFeedback(button, 'Ocurrió un error creando o enviando el mail: ' + jqXHR.responseText);
                })
            .success(
                function(response) {
                    if ('error' in response){
                        showNegativeFeedback(button,
                            'Ocurrió al menos un problema enviando el mail:\n'
                            + response['error'].split("|").map(x => "- ".concat(x)).join("\n")
                            + (response['log'] !== '' ? ('\n\nMostrando las últimas 20 líneas del log:\n\n' + response['log']) : ''));
                    }
                    else {
                        if (response['log'] === ''){
                            showPositiveFeedback(button, 'No se encontraron problemas enviando el mail, ' +
                                'pero no hay logs donde se pueda realizar un mayor análisis de errores.');
                        }
                        else {
                            showPositiveFeedback(button, 'Mail enviado exitosamente!');
                        }
                    }
                });
    });
});