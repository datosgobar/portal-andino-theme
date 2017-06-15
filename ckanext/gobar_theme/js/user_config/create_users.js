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
});