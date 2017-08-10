$(function () {
    var page = 1;
    $('.show-more').on('click', function (e) {
        var url = './historial.json';
        var data = {page: page+1, raw: true}
        var button = $(e.currentTarget);
        button.addClass('fetching');
        var callback = function (response) {
            var activities = $(response.activities).find('li.item')
            $('#user-config-history ul.activity').append(activities)
            var has_more = response.has_more
            if (!has_more) {
                button.addClass('hidden');
            } else {
                button.removeClass('fetching');
            }
            page += 1
        }
        var failCallback = function () { button.removeClass('fetching'); }
        $.get(url, data, callback).fail(failCallback);
    });

    $('.load-more').remove()
});
