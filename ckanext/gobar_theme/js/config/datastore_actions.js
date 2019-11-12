$(function() {

    $('#cron-enabler').on('click', function (e) {
        let checkbox = $(this).find('input[type=checkbox]');
        let is_checked = checkbox.prop('checked');

        $('select.datapusher').prop('disabled', is_checked);
        checkbox.prop('checked', !checkbox.prop('checked'));
        e.stopPropagation();
        e.preventDefault();
    });

});