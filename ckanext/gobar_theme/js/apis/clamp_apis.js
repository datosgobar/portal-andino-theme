$(function() {

    $('.dataset-title').each(function(index) {
        $clamp(this, {clamp: 1, useNativeClamp: true})
    });
    $('.dataset-notes').each(function(index) {
        $clamp(this, {clamp: 4, useNativeClamp: true})
    });

});
