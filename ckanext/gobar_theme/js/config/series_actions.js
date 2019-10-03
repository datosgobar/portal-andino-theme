$(function() {

    $('form').on('submit', function (e) {
        var validations = [validateLaps, validateMaxDecimals];
        cleanErrorLabels();

        for (var i = 0; i < validations.length; i++) {
            if (!validations[i]()) {
                e.preventDefault();
            }
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
        if (field.val() === '' || valueIsPositiveInteger(field.val())) {
            return true;
        }
        var errorText = "Se debe ingresar un número entero positivo.";
        showErrorOnField(field, errorText);
        return false;
    }

    function validateMaxDecimals() {
        var maxDecimalsInput = $('input[name="max-decimals"]');
        if (maxDecimalsInput.val() === '' || valueIsPositiveInteger(maxDecimalsInput.val())) {
            return true;
        }
        var errorText = "Se debe ingresar un número entero a partir de 0 (cero).";
        showErrorOnField(maxDecimalsInput, errorText);
        return false;
    }

});