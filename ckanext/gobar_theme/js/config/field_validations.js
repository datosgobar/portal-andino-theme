$(function validateSiteFields(){
    $(".site-config").on('click', function(e){
        e.preventDefault();
        if ($(".site-title").text().length < 9){
            $(".site-title-div").append('<span">El título no puede tener menos de 9 caracteres.</span>');
        }
    });
});
