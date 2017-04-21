$(function() {
    var scroll = 0;
    $(document).on('scroll', function() {
        scroll = $(document).scrollTop();
    });

    $('input[type="radio"]').on('click', function(e) {
        var box = $(e.currentTarget).parents('.radio-box');
        box.parents('.radio-container').find('.radio-box').removeClass('selected').addClass('not-selected');
        box.removeClass('not-selected').addClass('selected');
        $(document).scrollTop(scroll);
    });
});