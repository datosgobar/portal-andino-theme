$(function () {
    $('#portal-country').on('change', function () {
        var selected = $(this).find("option:selected").text();
        var x = 0;
        var elem = document.getElementsByClassName('from-country');
        if (selected === 'Argentina') {
            for (x = 0; x < elem.length; x++) {
                elem[x].style.display = 'block';
            }
        }
        else {
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

$(document).ready(function () {
    var country = $("#portal-country");
    var elem = document.getElementsByClassName('from-country');
    var x = 0;
    if (country.find(":selected").text() === 'Argentina') {
        for (x = 0; x < elem.length; x++) {
            elem[x].style.display = 'block';
        }
    }
    else {
        for (x = 0; x < elem.length; x++) {
            elem[x].style.display = 'none';
        }
    }
});

                                            // conseguir datos de municipios con ajax
// $(document).ready(function () {
//     var municipio_select = $("#portal-municipio");
//     var province_id = $("#portal-province").children(':selected').val();
//     var url_to_call = 'http://181.209.63.243/api/v1.0/municipios?max=100&provincia=' + province_id;
//     $.ajax({
//         type: "GET",
//         dataType: 'json',
//         url: 'https://cors-anywhere.herokuapp.com/' + url_to_call,
//         success: function (response) {
//             // municipio_select.find('option').remove();
//             response['municipios'].sort(function compare(a,b) {
//                 if (a.nombre < b.nombre)
//                     return -1;
//                 if (a.nombre > b.nombre)
//                     return 1;
//                 return 0;
//             });
//             console.log(response['municipios']);
//             var x = 0;
//             for (x = 0; x < response['municipios'].length; x++) {
//                 municipio_select.append('<option value=' + response['municipios'][x]['id'] + '>' + response['municipios'][x]['nombre'] + '</option>')
//             }
//         }
//     });
// });

function change_province() {
    var province_id = $('#portal-province').val();
    $(".municipio-option").each(function () {
        if ($(this).data('province') == province_id){       // no cambiar a '===', porque tiraría False siempre!
            $(this).show();
        }
        else{
            $(this).prop("selected", false);
            $(this).hide();
        }
    });
}


$('.municipio-option').mousedown(function(e) {
    e.preventDefault();
    $(this).prop('selected', !$(this).prop('selected'));
    return false;
});


$(document).ready(function () {
    change_province();
});