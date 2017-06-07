$(function () {
    var showEditSection = function (e) {
        var replaceId = $(e.currentTarget).parents('.disabled-input').addClass('hidden').data('replace-id');
        $('#' + replaceId).removeClass('hidden');
    };
    $('.disabled-input svg').click(showEditSection);


    var resetEditSection = function (editSection) {
        var inputs = editSection.find('input');
        for (var i=0; i<inputs.length; i++) {
            var $input = $(inputs[i]);
            $input.val($input.data('default-value') || '');
        }
        editSection.addClass('hidden')
        $('div[data-replace-id="' + editSection.attr('id') + '"]').removeClass('hidden');
    };
    $('#cancel-email, #cancel-password').click(function (e) {
        var editSection = $(e.currentTarget).parents('.edit-section');
        resetEditSection(editSection);
    });


    var sendChanges = function (editSection) {
        var inputs = editSection.find('input');
        var endpoint = editSection.data('endpoint');
        var data = {};
        data[editSection.data('attr')] = $(inputs[0]).val()
        var callback = function (response) {
            console.log(response)
            if(response.success) {
                console.log(response)
                window.location.reload()
            }
        };
        $.post(endpoint, data, callback);
    };

    var validate = function (editSection) {
        var inputs = editSection.find('input');
        var firstInput = $(inputs[0]);
        var secondInput = $(inputs[1]);
        var valuesAreEqual = firstInput.val() == secondInput.val();
        if (!valuesAreEqual) {
            showNegativeFeedback(secondInput, 'Los datos ingresados no coinciden');
            return false
        }
        var attr = editSection.data('attr');
        if (attr == 'password') {
            // TODO: validaciones de contraseña
        } else {
            // TODO: validaciones de mail
        }
        return true
    };

    var showPositiveFeedback = function(input, msg) {
        // TODO
    };

    var showNegativeFeedback = function (input, msg) {
        // TODO
    };

    var clearFeedback = function (input) {
        // TODO
    };

    $('#save-email, #save-password').click(function (e) {
        var editSection = $(e.currentTarget).parents('.edit-section');
        var isValid = validate(editSection);
        if (isValid) {
            sendChanges(editSection)
        }
    });
});