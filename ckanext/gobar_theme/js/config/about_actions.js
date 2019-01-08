$(function() {

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
        var new_div = createSectionDiv();
        $('button#add-another-section').before(new_div);
        writeDivIndexes();
    });

    $('form').on('submit', function (e) {

        function createErrorLabel (text, label_class){
            var newLabel = document.createElement('label');
            newLabel.appendChild(document.createTextNode(text));
            newLabel.className += label_class;
            newLabel.style.color = "red";
            newLabel.style.fontSize = "16px";
            newLabel.style.marginBottom = "30px";
            return newLabel;
        }

        function insertErrorForInput(current_div, current_input, text, label_class){
            if (current_div.find("label." + label_class).length === 0) { // si el div padre aún no tiene errores
                current_input.after(createErrorLabel(text, label_class));
                return true;
            }
            return false; // no hubo error --> no se agregó ningún label
        }

        if($('select').val() === 'Quiero secciones personalizadas (avanzado)'){
            var sections = [];
            var entered_filenames = [];
            var filename_error = false;
            var entered_titles = [];
            var entered_slugs = [];
            var title_error = false;
            var slug_error = false;
            var current_div;
            $('div.section-div').each(function () {
                var all_inputs = $(this).find('input');
                var title_input = "";
                var filename_input = "";
                var slug_input = "";
                var text = '';
                var label_class = '';
                var result = false;
                current_div = $(this);
                all_inputs.each(function () {
                    if ($(this).hasClass('about-section-title')) {
                        title_input = this.value;
                        label_class = 'title-error-message';
                        if(entered_titles.indexOf(title_input) >= 0){ // chequeo si este título ya fue ingresado
                            text = "Ya se ingresó un título idéntico a este.";
                            insertErrorForInput(current_div, $(this), text, label_class);
                            title_error = true;
                        }
                        else if(title_input.length === 0){
                            text = "El título está vacío.";
                            insertErrorForInput(current_div, $(this), text, label_class)
                            slug_error = true;
                        }
                        else {
                            entered_titles.push(title_input);
                            if($(this).next('label.title-error-message').length){
                                $(this).next('label.title-error-message').remove();
                            }
                        }
                    }
                    if ($(this).hasClass('about-section-slug')) {
                        slug_input = this.value;
                        label_class = 'slug-error-message';
                        if(slug_input.length === 0){
                            // Le doy un valor al slug en base al título y lo escribo en el input por si ya está en uso
                            // para que el usuario lo pueda ver cuando se muestre el error
                            slug_input = string_to_slug(title_input);
                            this.value = slug_input;
                        }
                        if(entered_slugs.indexOf(slug_input) >= 0){ // chequeo si este título ya fue ingresado
                            text = "Ya se ingresó un nombre de enlace idéntico a este.";
                            insertErrorForInput(current_div, $(this), text, label_class);
                            title_error = true;
                        }
                        else {
                            entered_slugs.push(slug_input);
                        }
                    }
                    if ($(this).hasClass('about-section-filename')) {
                        filename_input = this.value;
                        label_class = 'filename-error-message';
                        if(filename_input.length === 0){
                            text = "El nombre de archivo está vacío.";
                            insertErrorForInput(current_div, $(this), text, label_class);
                            filename_error = true;
                        }
                        else {
                            entered_filenames.push(filename_input);
                            if($(this).next('label.filename-error-message').length){
                                $(this).next('label.filename-error-message').remove();
                            }
                        }
                    }
                });

                if (title_input !== '' || filename_input !== '') {
                    var section = {title: title_input, filename: filename_input, slug: slug_input};
                    sections.push(section);
                }

            });
            if(filename_error || title_error || slug_error){
                e.preventDefault();
            }
            else{
                $('#about-sections').val(JSON.stringify(sections));
            }
        }
    });

    $(document).on('click', 'button.close', function () {
        var parent_div = $(this).parent();
        $('#delete-section-modal').modal(parent_div);

        $(document).on('click', '#delete-section-btn', function () {
            var isTheOnlyOne = $('div.section-div').length === 1;
            if (isTheOnlyOne) {
                parent_div.find('input').val('');  // Elimina los datos de la sección
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

    function createSectionDiv() {
        var div = $($('div.section-div')[0]).clone();
        div.find('input').val('');
        return div;
    }

    function string_to_slug (str) {
    str = str.replace(/^\s+|\s+$/g, ''); // trim
    str = str.toLowerCase();
    // remove accents, swap ñ for n, etc
    var from = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
    var to   = "aaaaeeeeiiiioooouuuunc------";
    for (var i=0, l=from.length ; i<l ; i++) {
        str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
    }
    str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
        .replace(/\s+/g, '-') // collapse whitespace and replace by -
        .replace(/-+/g, '-'); // collapse dashes

    return str;
}

});