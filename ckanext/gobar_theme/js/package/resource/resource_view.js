$(function () {
    $('a#embeber').on('click', function () {
        var id = $('a#embeber').data('module-resource-id')
         $.ajax({
            url: '/dataset/resource_view_embed/' + id,
            type: 'POST'
        });
    })
});
