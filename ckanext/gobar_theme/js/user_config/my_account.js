$(function () {
    $('.disabled-input svg').click(function (e) {
        var replaceId = $(e.currentTarget).parents('.disabled-input').addClass('hidden').data('replace-id');
        $('#' + replaceId).removeClass('hidden');
    });
    $('#cancel-email, #cancel-password').click(function (e) {
        var editSection = $(e.currentTarget).parents('.edit-section');
        var inputs = editSection.find('input');
        for (var i=0; i<inputs.length; i++) {
            var $input = $(inputs[i]);
            $input.val($input.data('default-value') || '');
        }
        editSection.addClass('hidden')
        $('div[data-replace-id="' + editSection.attr('id') + '"]').removeClass('hidden');
    });
    $('#save-email, #save-password').click(function () {

    });
});