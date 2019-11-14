$(function() {

    $(document).ready(function(){
        $('select.datapusher').prop('disabled', !$(this).find('input[type=checkbox]').prop('checked'));
    });

    $('input[name="enable_datastore_cron"]').on('change', function (e) {
        let is_checked = $(this).prop('checked');
        $('select.datapusher').prop('disabled', !is_checked);
        e.stopPropagation();
        e.preventDefault();
    });

});