$(function () {
    $('#greetings-modal').modal('show');
    $('#greetings-modal .dismiss-greetings').on('click', function() {
        $.post('/config/welcome', {});
        $('#greetings-modal').modal('hide');
    });
});