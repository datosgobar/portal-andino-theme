$(function () {
    var calls = $('.group-images img[data-replace="svg"]').replaceSVG();
    var callback = function () {
        setTimeout(function () {
            $('.search-filter, #search-results').removeClass('invisible')
            $('.dataset-title').each(function(index) {
                $clamp(this, {clamp: 2})
            });
            $('.dataset-author').each(function(index) {
                $clamp(this, {clamp: 1})
            });
            $('.dataset-notes').each(function(index) {
                $clamp(this, {clamp: 2})
            });
        }, 200)
    };
    $.when(calls).done(callback).fail(callback);
    
});
