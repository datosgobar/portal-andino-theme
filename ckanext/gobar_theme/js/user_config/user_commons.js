    var showPositiveFeedback = function (input, msg) {
        clearFeedback(input)
        if (msg && msg.length > 0) {
            var errormsg = $('<p class="feedback validation-success"></p>').text(msg)
            $(input).parent().append(errormsg)
        }
        var errorimg = $('<img src="/img/input-check.svg" class="feedback-img success">')
        $(input).parent().append(errorimg)
    };

    var showNegativeFeedback = function (input, msg) {
        clearFeedback(input)
        if (msg && msg.length > 0) {
            var errormsg = $('<p class="feedback validation-error"></p>').text(msg)
            $(input).parent().append(errormsg)
        }
        var errorimg = $('<img src="/img/input-error.svg" class="feedback-img">')
        $(input).parent().append(errorimg)
    };

    var clearFeedback = function (input) {
        $(input).parent().find('.feedback').remove()
        $(input).parent().find('.feedback-img').remove()
    };

    var email_re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

    $('button.delete-user').on('click', function () {
        if (!$(this).siblings('p.default-user-error').length && $(this).parents('div.edit-user-modal').data('username') === 'default') {
            $(this).after("<p class='default-user-error'>El usuario default no puede ser borrado.</p>");
        }
    });
