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
                            + (response['log'] !== undefined ? ('\n\nMostrando las últimas 10 líneas del log:\n\n' + response['log']) : ''));
                    }
                    else {
                        showPositiveFeedback(button, 'No se encontraron problemas enviando el mail!');
                    }
                });
    });
});