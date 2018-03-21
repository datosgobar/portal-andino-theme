$(function () {
    $('.header-link.dropdown').on('click', function (e) {
        var headerNav = $(e.currentTarget).toggleClass('active');
        e.stopPropagation();
        $('body').one('click', function () {
            headerNav.removeClass('active')
        });
    });

    $('#header .icon-reorder').on('click', function(e) {
        $('#header .xs-navbar').toggleClass('hidden')
        $('#header .icon-reorder').toggleClass('active')
        $('#header .logo-header').toggleClass('showing-nav')
    });

    $('#header .dropdown-navbar-link').on('click', function(e) {
        $(this).next().toggleClass('hidden');
    });

    $('.about-dropdown').each(function () {
        var total_li = $('.about-dropdown > a > li').length;
        var amount_to_substract = 0;
        if(total_li === 0){
            amount_to_substract = -40;
        }
        else{
            amount_to_substract = ((total_li - 3)*40).toString(); // -40px al bottom por cada li que contenga el menu
        }
        $(this).css('bottom', "-=" + amount_to_substract);
    });
});