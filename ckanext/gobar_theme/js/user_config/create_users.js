$(function () {
    $('.user-editable').on('click', function (e) {
        $(e.currentTarget).parents('.user').find('.modal').modal('show');
    });
    $('.user-list .modal .delete-user').on('click', function (e) {
        var username = $(e.currentTarget).parents('.modal').data('username');
        $.post('/configurar/borrar_usuario', {id: username}, function (response) {
            if (response.success) {
                window.location.reload()
            }
        })
    });

    $('.organization-select').multipleSelect({
        placeholder: "Elegí una o mas organizaciones.",
        filter: true,
        selectAll: false
    });

    $('input[name="username"]').on('change input keypress', function (e) {
        var $input = $(e.currentTarget);
        var remainingCaracters = 10 - $input.val().length;
        var text = $input.val().length == 0 ? 'Máximo 10 caracteres.' : 'Restan ' + remainingCaracters.toString() + ' caracter' + (remainingCaracters == 1 ? '' : 'es')
        $input.parent().siblings('.username-restriction').text(text)
        clearFeedback($input)
    })


    var validateSection = function (createSection) {
        var usernameInput = createSection.find('input[name="username"]')
        var nameInput = createSection.find('input[name="fullname"]')
        var emailInput = createSection.find('input[name="email"]')

        clearFeedback(usernameInput)
        clearFeedback(emailInput)
        clearFeedback(nameInput)

        if (usernameInput.val().length == 0) {
            showNegativeFeedback(usernameInput, 'Completá este dato.')
            return false
        }
        if (nameInput.val().length == 0) {
            showNegativeFeedback(nameInput, 'Completá este dato.')
            return false
        }
        if (emailInput.val().length == 0) {
            showNegativeFeedback(emailInput, 'Completá este dato.')
            return false
        }
        if (!email_re.test(emailInput.val())) {
            showNegativeFeedback(emailInput, 'Usá este formato nombre@ejemplo.com.');
            return false;
        }
        if (createSection.hasClass('user')) {
            var selectedOrganizations = createSection.find('select.organization-select').multipleSelect('getSelects');
            var divSelect = createSection.find('div.organization-select')
            clearFeedback(divSelect)
            if (selectedOrganizations.length == 0) {
                showNegativeFeedback(divSelect, 'Completá este dato.')
            }
        }
    };

    $('.save-new-user').on('click', function (e) {
        var createSection = $(e.currentTarget).parents('.create-section')
        var isValid = validateSection(createSection);
        if (isValid) {
            var data = {

            }
        }
    })
});