$(window).on('load', function () {
    show_specific_content($('select').val());
})

$('select').on('change', function(e) {
    show_specific_content($('select').val());
});

function show_specific_content(selected_value){
    if (selected_value === 'No quiero una sección de acerca'){
        $('div.basic-about').css('display', 'none');
        $('div.advanced-about').css('display', 'none');
    }
    else if(selected_value === 'Quiero una sección de acerca que dé información básica'){
        $('div.basic-about').css('display', 'block');
        $('div.advanced-about').css('display', 'none');
    }
    else if (selected_value === 'Quiero secciones personalizadas (avanzado)'){
        $('div.basic-about').css('display', 'none');
        $('div.advanced-about').css('display', 'block');
    }
}