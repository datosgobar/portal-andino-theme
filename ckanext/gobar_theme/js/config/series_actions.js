$(function() {

    $('form').on('submit', function (e) {
        cleanErrorLabels();

        if (!validateLaps()) {
            e.preventDefault();
        }
    });

    function validateLaps() {
        var lapDiariaInput = $('input[name="diaria"]');
        var lapMensualInput = $('input[name="mensual"]');
        var lapTrimestralInput = $('input[name="trimestral"]');
        var lapSemestralInput = $('input[name="semestral"]');
        var lapAnualInput = $('input[name="anual"]');
        var fields = [lapDiariaInput, lapMensualInput, lapTrimestralInput, lapSemestralInput, lapAnualInput];

        for (var i = 0; i < fields.length; i++) {
            if (!validateLapField(fields[i])) {
                return false;
            }
        }
        return true;
    }

    function validateLapField(field) {
        if (field.val() === '' || field.val() > 0) {
            return true;
        }
        var errorText = "Se debe ingresar un número entero positivo.";
        showErrorOnField(field, errorText);
        return false;
    }

    function showErrorOnField(field, errorText) {
        field.after(createErrorLabel(errorText));
    }

    function createErrorLabel(text) {  // TODO: llevar a archivo genérico
        var newLabel = document.createElement('label');
        newLabel.appendChild(document.createTextNode(text));
        newLabel.className += "input-error";
        return newLabel;
    }

    function cleanErrorLabels() {  // TODO: llevar a archivo genérico
        $('label.input-error').remove();
    }

});