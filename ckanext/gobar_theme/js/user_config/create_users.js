$(function () {
    $('.user-editable').on('click', function (e) {
        console.log(e)
        $(e.currentTarget).parents('.user').find('.modal').modal('show');
    })
});