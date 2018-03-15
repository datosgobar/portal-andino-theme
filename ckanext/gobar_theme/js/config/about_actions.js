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
        if($('select').val() === 'Quiero secciones personalizadas (avanzado)'){
            var sections = [];
            var filenames = [];
            var repeated_filename = false;
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
                        if(filenames.indexOf(filename_input) >= 0){
                            if (!document.getElementById("error-launch-date")) { // if parent doesn't have error messages
                                var newLabel = document.createElement('label');
                                var text = document.createTextNode("Ya se ingresó un nombre de archivo idéntico a este.");
                                newLabel.appendChild(text);
                                newLabel.className += 'filename-error-message';
                                newLabel.style.color = "red";
                                newLabel.style.fontSize = "16px";
                                newLabel.style.marginBottom = "30px";
                                $(this).after(newLabel);
                            }
                            repeated_filename = true;
                        }
                        else {
                            filenames.push(filename_input);
                            if($(this).next('label.filename-error-message').length){
                                $(this).next('label.filename-error-message').remove();
                            }
                        }
                    }
                });

                if (title_input !== '' || filename_input !== '') {
                    var section = {title: title_input, fileName: filename_input};
                    sections.push(section);
                }

            });
            if(repeated_filename){
                alert("NO HAGO NADA");
                e.preventDefault();
            }
            else{
                alert("Joya.");
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

});