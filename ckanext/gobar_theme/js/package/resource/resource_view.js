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
        $('.col_title').each(function(index, element) {
            element.style.setProperty( 'width', '13%', 'important' );
        });
        $('.type').each(function(index, element) {
            element.style.setProperty( 'width', '7%', 'important' );
        });
        $('.description').each(function(index, element) {
            element.style.setProperty( 'width', '34%', 'important' );
        });
        $('.units').each(function(index, element) {
            element.style.setProperty( 'width', '16%', 'important' );
        });
        $('.id').each(function(index, element) {
            element.style.setProperty( 'width', '17%', 'important' );
        });
        $('.specialType').each(function(index, element) {
            element.style.setProperty( 'width', '7%', 'important' );
        });
        $('.specialTypeDetail').each(function(index, element) {
            element.style.setProperty( 'width', '6%', 'important' );
            element.style.setProperty( 'padding-right', '0', 'important' );
        });
    }
});