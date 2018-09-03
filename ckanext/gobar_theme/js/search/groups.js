$(function () {
    var calls = $('.group-images img[data-replace="svg"]').replaceSVG();
    var callback = function () {
        setTimeout(function () {
            $('.search-filter, #search-results').removeClass('invisible')
        }, 200)
    };
    $.when(calls).done(callback).fail(callback);

    $('.dataset-title').each(function(index) {
        $clamp(this, {clamp: 2, useNativeClamp: false})
    });
    $('.dataset-author').each(function(index) {
        $clamp(this, {clamp: 1, useNativeClamp: false})
    });
    $('.dataset-notes').each(function(index) {
        $clamp(this, {clamp: 2, useNativeClamp: false})
    });
});
