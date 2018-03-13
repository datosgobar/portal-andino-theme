$(window).on('load', function () {
    show_specific_content($('select').val());
});

$('select').on('change', function () {
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
        writeDivIndexes();
    }
}

$('button#add-another-section').on('click', function (e) {
    e.preventDefault();
    var new_div = '<div class="section-div"><button type="button" class="close" aria-label="Close"><span aria-hidden="true">x</span></button><h2 class="section">Sección</h2><hr class="section"><h2>Título</h2><input class="about-section-title" name="about-section-title" type="text" title="Título" value=""><h2>Nombre del archivo</h2><input class="about-section-filename" name="about-section-filename" type="text" title="Nombre del archivo" value=""></div>';
    $('button#add-another-section').before(new_div);
    writeDivIndexes();
});

$('form').on('submit', function () {
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

        var section = {title: title_input, fileName: filename_input};
        sections.push(section);
    });
    $('#about-sections').val(JSON.stringify(sections));
});

$('button.close').on('click', function () {
    var parent_div = $(this).parent();
    $('#delete-section-modal').modal(parent_div);

    $(document).on('click', '#delete-section-btn', function () {
        var isTheOnlyOne = $('div.section-div').length === 1;
        if (isTheOnlyOne) {
            parent_div.find('input').val('');  // Elimina los datos de la sección  todo: chequear que una seccion no se envie vacia
        } else {
            parent_div.remove();
        }
        writeDivIndexes();
    });

});

function writeDivIndexes() {
    var cont = 1;
    $('div.section-div').each(function () {
        var section_h2 = $(this).find('h2.section');
        section_h2.text("Sección " + cont);
        cont += 1;
    });
}