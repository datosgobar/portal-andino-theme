$(function () {
    var page = 1;
    $('.show-more').on('click', function (e) {
        var url = window.location.href;
        var data = {page: page+1, raw: true}
        var button = $(e.currentTarget);
        button.addClass('fetching');
        var callback = function (response, textStatus, request) {
            var activities = $(response).find('li.item')
            $('#user-config-history ul.activity').append(activities)
            var has_more = request.getResponseHeader('X-has-more') == 'True';
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
});