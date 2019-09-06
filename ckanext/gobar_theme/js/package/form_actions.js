function validLength(length, maxLength) {
    return maxLength >= length;
}

function validTitle(){
    var titleLength = $('input[data-valid-title-length]').val().length;
    var validTitleLength = $('input[data-valid-title-length]').data('valid-title-length');
    return validLength(titleLength, validTitleLength);
}

function validDesc(){
    var descLength = $('textarea[data-valid-desc-length]').val().length
    var validDescLength = $('textarea[data-valid-desc-length]').data('valid-desc-length')
    return validLength(descLength, validDescLength);
}

function validateTitle() {
    $('input#field-title').parent('div').children('div#field-title').toggleClass('long-field', !validTitle());
}

function validateDesc() {
    $('div#field-notes.after-desc').toggleClass('long-field', !validDesc());
}

$(function () {
    var $form;

    function addGroupValues() {
        var checkboxList = $('.package-group-checkbox:checked');
        for (var i = 0; i < checkboxList.length; i++) {
            var $checkbox = $(checkboxList[i]);
            var hiddenGroup = $('<input type="hidden">');
            hiddenGroup.attr('name', 'groups__' + i.toString() + '__name');
            hiddenGroup.val($checkbox.attr('id'));
            $form.append(hiddenGroup);
        }
    }

    function addGlobalGroupValues() {
        var checkboxList = $('.package-global-group-checkbox:checked');
        var values = [];
        for (var i = 0; i < checkboxList.length; i++) {
            var $checkbox = $(checkboxList[i]);
            values.push($checkbox.attr('id'));
        }
        values = JSON.stringify(values);
        addExtra('superTheme', values)
    }

    var extraCounter = 0;

    function addExtra(key, value) {
        var hiddenKey = $('<input type="hidden">').attr({
            type: 'hidden',
            name: 'extras__' + extraCounter.toString() + '__key',
            value: key
        });
        var hiddenValue = $('<input type="hidden">').attr({
            type: 'hidden',
            name: 'extras__' + extraCounter.toString() + '__value',
            value: value
        });
        var extrasContainer = $('.hidden-extras-container');
        extrasContainer.append(hiddenKey);
        extrasContainer.append(hiddenValue);
        extraCounter += 1;
    }

    function addDates() {
        var dateFrom = $('#date-from').datepicker('getDate');
        var dateTo = $('#date-to').datepicker('getDate');
        var value = '';
        if (dateFrom) {
            value = dateFrom.toISOString();
        }
        if (dateTo) {
            value += '/' + dateTo.toISOString();
        }
        addExtra('temporal', value);
    }

    function addHiddenExtras() {
        var extras = $('.hidden-extra input, .hidden-extra-select select');
        for (var i = 0; i < extras.length; i++) {
            var extra = $(extras[i]);
            var inputType = extra.attr('type');
            var name = extra.attr('name');
            if (!name) {
                continue;
            }
            var value;
            if (inputType == 'text') {
                value = extra.val();
            } else if (inputType == 'checkbox') {
                value = extra.is(':checked').toString()
            } else if (inputType == 'select') {
                if (extra.attr('multiple') == 'multiple') {
                    var selectedOptions = extra.find('option:selected');
                    value = [];
                    for (var j = 0; j < selectedOptions.length; j++) {
                        value.push($(selectedOptions[j]).val());
                    }
                    value = JSON.stringify(value);
                } else {
                    value = extra.find('option:selected').val();
                }

            }
            addExtra(name, value);
        }
    }

    function addSaveHidden() {
        var hiddenSave = $('<input type="hidden" name="save">');
        $form.append(hiddenSave);
    }

    function formIsValid() {
        $('.missing-field').remove();
        var isValid = true;
        var errorTemplate = '<div class="missing-field">Completá este dato</div>';

        var title = $('#field-title');
        if (!title.val().length > 0) {
            isValid = false;
            title.after(errorTemplate)
        }

        var description = $('#field-notes');
        if (!description.val().length > 0) {
            isValid = false;
            description.after(errorTemplate)
        }

        if (!$('.package-global-group-checkbox:checked').length > 0) {
            isValid = false;
            $('.super-groups').append(errorTemplate);
        }

        var author = $('#field-author');
        if (!author.val().length > 0) {
            isValid = false;
            author.after(errorTemplate);
        }

        var updateFreq = $('#update-freq');
        if (!updateFreq.val()) {
            isValid = false;
            updateFreq.after(errorTemplate);
        }

        isFormValid = isValid && validTitle() && validDesc()

        if (!isFormValid) {
            window.scrollTo(0, 0);
        }

        return isFormValid;
    }

    $('form#dataset-edit').submit(function (e) {
        $form = $(this);
        if (formIsValid()) {
            addGroupValues();
            addGlobalGroupValues();
            addHiddenExtras();
            addDates();
            return true
        }
        return false
    });

    $('#save-draft').on('click', function () {
        $('#visibility').val('False');
        $form = $('form#dataset-edit');
        addSaveHidden();
        $form.attr('action', '/dataset/new_draft').submit();
    });

    $('#date-from, #date-to').datepicker({
        language: 'es'
    });

    $('#date_with_time').on('change', function (e) {
        var showHours = $(e.currentTarget).is(':checked');
        $('.hour-picker-to, .hour-picker-from').toggleClass('hidden', !showHours);
    });

    var dates = $('.date-picker').data('dates');
    var dateFrom, dateTo;
    if (dates.indexOf('/')) {
        dates = dates.split('/');
        dateFrom = new Date(dates[0]);
        dateTo = new Date(dates[1]);
    } else {
        dateFrom = new Date(dates);
    }
    if (dateFrom instanceof Date && isFinite(dateFrom)) {
        $('#date-from').datepicker('setDate', dateFrom);
    }
    if (dateTo instanceof Date && isFinite(dateTo)) {
        $('#date-to').datepicker('setDate', dateTo);
    }

    $(document).ajaxComplete(function(){
        $('.slug-preview').each(function() {
            $(this).insertAfter($('div#field-title'));
        });
    });

    $(document).ready(function(){
        $('input[data-valid-title-length]').on('change input keyup', validateTitle)
        validateTitle()

        $('textarea[data-valid-desc-length]').on('change input keyup', validateDesc)
        validateDesc()
     });



    var interval = setInterval(function() {
        var urlPreview = $('.slug-preview');
        if (urlPreview.length > 0) {
            clearInterval(interval);
        }
    }, 100);

});

$(document).ready( function(){
    $('#field-name').bind("keyup change", function() {
        if (!$('#field-url').attr("was_edited")) {
            var myDomElement = document.getElementsByClassName( "slug-preview-value" );
            var field_url = '';
            setTimeout(function () {
                if ($(myDomElement).text() === $('#field-name').val()){
                    field_url = $('#field-url').attr("domain") + $(myDomElement).text();
                }
                else{
                    field_url = $('#field-url').attr("domain") + $('#field-name').val();
                }
                field_url = field_url.replace(/-+/g, '-');
                if (field_url[0] === '-') {
                    field_url = field_url.substr(1);
                }
                $('#field-url').val(field_url);
            }, 1000);
        }
    });
});

$(document).ready( function(){
    $('#dataset-edit').on("submit", function(e) {
        var regex = new RegExp(
            /^(localhost|http:\/\/localhost|https:\/\/localhost)|(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)[a-z0-9]+([\-.]{1}[a-z0-9]+)*(\.[a-z0-9]{2,5}|(:[0-9]{1,5}))(\/.*)?$/
        );
        if (!$('#field-url').val().match(regex)) {
            e.preventDefault();
            if (!document.getElementById("error-field-url")){
                var newSpan = document.createElement('label');
                var text = document.createTextNode("La URL ingresada no es válida");
                newSpan.appendChild(text);
                newSpan.setAttribute("id", "error-field-url");
                newSpan.style.color = "red";
                newSpan.style.fontSize = "16px";
                newSpan.style.marginTop = "5px";
                $("#field-url").after(newSpan);
            }
        }
        else{
            if (document.getElementById("error-field-url")){
                document.getElementById("error-field-url").remove();
            }
        }
    });
});