$(function () {
    $('a#embeber').on('click', function () {
        var id = $('a#embeber').data('module-resource-id');
         $.ajax({
            url: '/dataset/resource_view_embed/' + id,
            type: 'POST'
        });
    })
});

$(window).load(function(){
    var body =  $('#metadata-table > tbody');
    if (body.get(0).scrollHeight > body.height()){
        $('.description').each(function(index, element) {
            element.style.setProperty( 'width', '34%' );
        });
        $('.specialTypeDetail').each(function(index, element) {
            element.style.setProperty( 'width', '6%' );
            element.style.setProperty( 'padding-right', '0' );
        });
    }
});