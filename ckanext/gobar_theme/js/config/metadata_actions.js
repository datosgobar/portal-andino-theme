$("#submit-metadata-portal").click(function (e) {
    var launch_date = document.getElementsByName("metadata-launch_date");
    var error_found = false;
    if ($(launch_date).val() !== '') {
        date_to_parse = convert_ddmmyyyy_to_mmddyyyy($(launch_date).val());
        if (isNaN(parseFloat(Date.parse(date_to_parse)))) {
            error_found = true;
            e.preventDefault();
            if (!document.getElementById("error-launch-date")) {
                var newSpan = document.createElement('label');
                var text = document.createTextNode("La fecha ingresada no es válida");
                newSpan.appendChild(text);
                newSpan.setAttribute("id", "error-launch-date");
		        newSpan.className += 'form-error-message';
                newSpan.style.color = "red";
                newSpan.style.fontSize = "16px";
                newSpan.style.marginBottom = "30px";
                $(launch_date).after(newSpan);
            }
            $('html, body').animate({
                scrollTop: $(launch_date).offset().top - 150
            }, 2);
        }
    }
    if (!error_found){
        if (document.getElementById("error-launch-date")) {
            document.getElementById("error-launch-date").remove();
        }
    }
});

function convert_ddmmyyyy_to_mmddyyyy(date) {
    if (date.length !== 10 || date.charAt(2) !== date.charAt(5)) {
        // una fecha válida debe tener 10 caracteres, y debe escribirse usando '-' o '/' ambas veces
        return null;
    }
    // Date.parse(...) utiliza el formato mm/dd/yyyy, mientras que nosotros utilizamos dd/mm/yyyy
    month = date.charAt(3) + date.charAt(4);
    day = date.charAt(0) + date.charAt(1);
    year = date.charAt(6) + date.charAt(7) + date.charAt(8) + date.charAt(9);
    return month + date.charAt(2) + day + date.charAt(5) + year;
}







$(function () {

    // var dateFrom = $('#date-from').datepicker('getDate');
    // if (dateFrom) {
    //     var withHours = $('#date_with_time').is(':checked');
    //     if (withHours && dateFrom) {
    //         var hoursFrom = $('#date-from-hour option:selected').val();
    //         var minutesFrom = $('#date-from-minute option:selected').val();
    //         dateFrom.setHours(hoursFrom, minutesFrom);
    //     }
    //     var value = '';
    //     if (dateFrom) {
    //         value = dateFrom.toISOString();  TODO: este bloque hace que el calendario aparezca siempre en inglés y necesito que esté en español
    //     addExtra('dateRange', value);        TODO: además, acá necesito pegarle la hora y los minutos para que esté en el data.json
    // }                                        TODO: ver qué parte del bloque hace que funcione mal


    $('#date-from').datepicker({
        language: 'es'
    });

    var dates = $('.date-picker').data('dates');
    var dateFrom;
    if (dates.indexOf('/')) {
        dates = dates.split('/');
        dateFrom = new Date(dates[0]);
    } else {
        dateFrom = new Date(dates);
    }
    if (dateFrom instanceof Date && isFinite(dateFrom)) {
        $('#date-from').datepicker('setDate', dateFrom);
        var hoursFrom = dateFrom.getHours();
        var minutesFrom = dateFrom.getMinutes();
        if (hoursFrom != 0 || minutesFrom != 0) {
            hoursFrom = hoursFrom < 10 ? '0' + hoursFrom : hoursFrom.toString();
            minutesFrom = minutesFrom < 10 ? '0' + minutesFrom : minutesFrom.toString();
            $('#date_with_time').prop('checked', true);
            $('#date-from-hour').val(hoursFrom);
            $('#date-from-minute').val(minutesFrom);
        }
    }

    $('#date_with_time').on('change', function (e) {
        var showHours = $(e.currentTarget).is(':checked');
        $('.hour-picker-from').toggleClass('hidden', !showHours);
    });

});