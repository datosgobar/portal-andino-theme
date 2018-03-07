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
    $('#date-from').datepicker({
        language: 'es',
        today: "Hoy"
    });
});