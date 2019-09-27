$(function () {
    var multipleSelectOptions = {
        placeholder: "Elegí una o mas organizaciones.",
        filter: true,
        selectAll: false,
        minimumCountSelected: 2
    }
    $('.create-section .organization-select').multipleSelect(multipleSelectOptions);
    multipleSelectOptions['maxHeight'] = 92;
    $('.modal .organization-select').multipleSelect(multipleSelectOptions);

    $('.modal').each(function (i, el) {
        var $el = $(el);
        var roleSelector = $el.find('select.user-role');
        roleSelector.data('role', roleSelector.val());
        var organizationSelector = $el.find('select.organization-select');
        organizationSelector.data('organizations', organizationSelector.multipleSelect('getSelects'))
    });
    $('.user-editable').on('click', function (e) {
        $(e.currentTarget).parents('.user').find('.modal').modal('show');
    });
    $('.user-list .modal .delete-user').on('click', function (e) {
        var username = $(e.currentTarget).parents('.modal').data('username');
        var button = $(e.currentTarget);
        button.prop('disabled', true);
        var failCallback = function () { button.prop('disabled', false); };
        $.post('/configurar/borrar_usuario', {id: username, token: $("#token-generator input").val()}, function (response) {
            if (response.success) {
                window.location.reload()
            }
            button.prop('disabled', false);
        }).fail(failCallback);
    });
    $('.modal .save-edit').on('click', function (e) {
        var button = $(e.currentTarget);
        var $el = $(e.currentTarget).parents('.modal')
        var data = {
            username: $el.find('input[name="username"]').val(),
            role: $el.find('select.user-role').val(),
            organizations: $el.find('select.organization-select').multipleSelect('getSelects'),
            token: $("#token-generator input").val()
        }
        var callback = function (response) {
            if (response.success) {
                window.location.reload()
            }
            button.prop('disabled', false);
        }
        var failCallback = function () {
            button.prop('disabled', false);
        }
        button.prop('disabled', true);
        $.post('/configurar/editar_usuario', data, callback).fail(failCallback);
    })
    $('.modal .cancel-edit').on('click', function (e) {
        var $el = $(e.currentTarget).parents('.modal');
        var roleSelector = $el.find('select.user-role');
        roleSelector.val(roleSelector.data('role')).trigger('change');
        var organizationSelector = $el.find('select.organization-select');
        organizationSelector.multipleSelect('setSelects', organizationSelector.data('organizations'));
    })
    $('.modal select.user-role').on('change', function (e) {
        var role = $(e.currentTarget).val()
        $(e.currentTarget).siblings('.user-edit-organizations').toggleClass('hidden', role == 'admin')
    });


    $('input[name="username"]').on('change input keypress', function (e) {
        var $input = $(e.currentTarget);
        var remainingCaracters = 60 - $input.val().length;
        var text = $input.val().length === 0 ? 'Máximo 60 caracteres.' : 'Restan ' + remainingCaracters.toString() + ' caracter' + (remainingCaracters === 1 ? '' : 'es');
        $input.parent().siblings('.username-restriction').text(text)
        clearFeedback($input)
    })


    var validateSection = function (createSection) {
        var usernameInput = createSection.find('input[name="username"]');
        var nameInput = createSection.find('input[name="fullname"]');
        var emailInput = createSection.find('input[name="email"]');
        var passwordInput = createSection.find('input[name="password"]');
        var repeatedPasswordInput = createSection.find('input[name="password2"]');

        clearFeedback(usernameInput);
        clearFeedback(emailInput);
        clearFeedback(nameInput);
        clearFeedback(passwordInput);
        clearFeedback(repeatedPasswordInput);

        if (usernameInput.val().length < 2) {
            showNegativeFeedback(usernameInput, 'Debe tener al menos 2 caracteres de longitud.');
            return false
        }
        if (passwordInput.val() !== '' && !securePassword(passwordInput.val())) {
            insecurePasswordMessage(passwordInput);
            return false;
        }
        if (passwordInput.val() !== repeatedPasswordInput.val()) {
            showNegativeFeedback(repeatedPasswordInput, '¡Oh! Las contraseñas no coinciden. Probá otra vez.');
            return false;
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
                return false
            }
        }
        return true
    };

    $('.save-new-user').on('click', function (e) {
        var createSection = $(e.currentTarget).parents('.create-section')
        var isValid = validateSection(createSection);
        var usernameInput = createSection.find('input[name="username"]');
        var passwordInput = createSection.find('input[name="password"]');
        var repeatedPasswordInput = createSection.find('input[name="password2"]');
        var fullnameInput = createSection.find('input[name="fullname"]');
        var emailInput = createSection.find('input[name="email"]');
        var button = $(e.currentTarget);
        if (isValid) {
            var data = {
                username: usernameInput.val().trim(),
                password: passwordInput.val().trim(),
                fullname: fullnameInput.val().trim(),
                email: emailInput.val().trim(),
                token: $("#token-generator input").val()
            }
            if (createSection.hasClass('user')) {
                var organizationSelect = createSection.find('select.organization-select');
                data['organizations'] = organizationSelect.multipleSelect('getSelects');
            } else {
                data['admin'] = true
            }
            var url = window.location.href;
            button.prop('disabled', true);
            var failCallback = function () { button.prop('disabled', false); };
            $.post(url, data, function (response) {
                button.prop('disabled', false);
                if (response.success) {
                    showPositiveFeedback(usernameInput);
                    showPositiveFeedback(fullnameInput);
                    showPositiveFeedback(passwordInput);
                    showPositiveFeedback(repeatedPasswordInput);
                    if (createSection.hasClass('admin')) {
                        showPositiveFeedback(emailInput, '¡Perfecto! Creaste un nuevo usuario.');
                    } else {
                        showPositiveFeedback(emailInput);
                        showPositiveFeedback(organizationSelect, '¡Perfecto! Creaste un nuevo usuario.');
                    }

                } else if (response.error == 'user_already_exists') {
                    showNegativeFeedback(usernameInput, 'Este usuario ya existe.');
                }
            }).fail(failCallback)
        }
    });
});
