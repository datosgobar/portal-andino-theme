$(function () {
    $('#portal-country').on('change', function () {
        var selected = $(this).find("option:selected").text();
        var x = 0;
        if (selected === 'Argentina') {
            var elem = document.getElementsByClassName('portal-province');
            for (x = 0; x < elem.length; x++) {
                elem[x].style.display = 'block';
            }
        }
        else {
            elem = document.getElementsByClassName('portal-province');
            for (x = 0; x < elem.length; x++) {
                elem[x].style.display = 'none';
            }
        }
    });
});

$("#submit-metadata-portal").click(function (e) {
    var launch_date = document.getElementsByName("metadata-launch_date");
    if ($(launch_date).val() !== '') {
        date_to_parse = convert_ddmmyyyy_to_mmddyyyy($(launch_date).val());
        if (isNaN(parseFloat(Date.parse(date_to_parse)))) {
            e.preventDefault();
            console.log("Texto: " + date_to_parse);
            console.log("Fecha parseada: " + Date.parse(launch_date.text));
            if (!document.getElementById("error-launch-date")) {
                var newSpan = document.createElement('label');
                var text = document.createTextNode("La fecha ingresada no es válida");
                newSpan.appendChild(text);
                newSpan.setAttribute("id", "error-launch-date");
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
});

function convert_ddmmyyyy_to_mmddyyyy(date) {
    if (date.length !== 10 || date.charAt(2) !== date.charAt(5)){
        // una fecha válida debe tener 10 caracteres, y debe escribirse usando '-' o '/' ambas veces
        return null;
    }
    // Date.parse(...) utiliza el formato mm/dd/yyyy, mientras que nosotros utilizamos dd/mm/yyyy
    month = date.charAt(3) + date.charAt(4);
    day = date.charAt(0) + date.charAt(1);
    year = date.charAt(6) + date.charAt(7) + date.charAt(8) + date.charAt(9);
    return month + date.charAt(2) + day + date.charAt(5) + year;
}