$(window).on('load', function () {
    show_specific_content($('select').val());
});

$('select').on('change', function (e) {
    show_specific_content($('select').val());
});

function show_specific_content(selected_value) {
    if (selected_value === 'No quiero una sección de acerca') {
        $('div.basic-about').css('display', 'none');
        $('div.advanced-about').css('display', 'none');
    }
    else if (selected_value === 'Quiero una sección de acerca que dé información básica') {
        $('div.basic-about').css('display', 'block');
        $('div.advanced-about').css('display', 'none');
    }
    else if (selected_value === 'Quiero secciones personalizadas (avanzado)') {
        $('div.basic-about').css('display', 'none');
        $('div.advanced-about').css('display', 'block');
    }
}

$('form').on('submit', function (e) {
    var sections = [];
    $('div.section-div').each(function () {
        var all_inputs = $(this).find('input');
        var title_input = "";
        var filename_input = "";

        all_inputs.each(function () {
            if ($(this).hasClass('about-section-title')) {
                title_input = this.value;
            }
            if ($(this).hasClass('about-section-filename')) {
                filename_input = this.value;
            }
        });

        // var section = JSON.stringify({title: title_input, fileName: filename_input});
        var section = '{'
            + '"title": ' + title_input + ','
            + '"fileName": ' + filename_input
            + '}';
        sections.push(section);
    });
    $('#about-sections').val(sections);
});


// $('form').on('submit', function (e) {
//     alert("empiezo");
//     var sections = [];
//     // $('div.section-div').each(function (i, obj) {
//         $('div.section-div input').each(function () {
//             if($(this).hasClass('about-section-title')){
//                 alert("Título: " + this.value);
//             }
//             if($(this).hasClass('about-section-filename')){
//                 alert("Filename: " + this.value);
//             }
// });
//     var title_input = obj.getElementsByClassName("about-section-title")[0].val();
//     alert(title_input);
//     var filename_input = obj.getElementsByClassName("about-section-filename")[0].val();
//     alert(filename_input);
//     // var section = '{'
//     //                 + '"title": ' + title_input + ','
//     //                 + '"fileName: ' + filename_input
//         //     //             + '}';
//         //     var section = JSON.stringify({title: title_input, fileName: filename_input});
//         //     sections.push(section);
//     });
// });