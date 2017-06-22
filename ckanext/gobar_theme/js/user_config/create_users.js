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
        $.post('/configurar/borrar_usuario', {id: username}, function (response) {
            if (response.success) {
                window.location.reload()
            }
        })
    });
    $('.modal .save-edit').on('click', function (e) {
        var $el = $(e.currentTarget).parents('.modal')
        var data = {
            username: $el.find('input[name="username"]').val(),
            role: $el.find('select.user-role').val(),
            organizations: $el.find('select.organization-select').multipleSelect('getSelects')
        }
        var callback = function (response) {
            if (response.success) {
                window.location.reload()
            }
        }
        $.post('/configurar/editar_usuario', data, callback);
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
        return true
    };

    $('.save-new-user').on('click', function (e) {
        var createSection = $(e.currentTarget).parents('.create-section')
        var isValid = validateSection(createSection);
        var usernameInput = createSection.find('input[name="username"]');
        var fullnameInput = createSection.find('input[name="fullname"]');
        var emailInput = createSection.find('input[name="email"]');
        if (isValid) {
            var data = {
                username: usernameInput.val().trim(),
                fullname: fullnameInput.val().trim(),
                email: emailInput.val().trim(),
            }
            if (createSection.hasClass('user')) {
                var organizationSelect = createSection.find('select.organization-select');
                data['organizations'] = organizationSelect.multipleSelect('getSelects');
            } else {
                data['admin'] = true
            }
            var url = window.location.href;
            $.post(url, data, function (response) {
                console.log(response)
                if (response.success) {
                    showPositiveFeedback(usernameInput)
                    showPositiveFeedback(fullnameInput)
                    if (createSection.hasClass('admin')) {
                        showPositiveFeedback(emailInput, '¡Perfecto! Creaste un nuevo usuario.')
                    } else {
                        showPositiveFeedback(emailInput)
                        showPositiveFeedback(organizationSelect, '¡Perfecto! Creaste un nuevo usuario.')
                    }

                } else if (response.error == 'user_already_exists') {
                    showNegativeFeedback(usernameInput, 'Este usuario ya existe.')
                }
            })
        }
    });
});