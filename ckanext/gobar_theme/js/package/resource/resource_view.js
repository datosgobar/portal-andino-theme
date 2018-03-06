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

    function columnHasSomething(string){
        var flag = 0;
        $(string).each(function(index) {
            if ($(this).text().trim().length){
                flag = 1;
                return false;
            }
        });
        return flag;
    }

    function getScrollbarWidth() {
        var outer = document.createElement("div");
        outer.style.visibility = "hidden";
        outer.style.width = "100px";
        outer.style.msOverflowStyle = "scrollbar"; // needed for WinJS apps
        document.body.appendChild(outer);
        var widthNoScroll = outer.offsetWidth;
        // force scrollbars
        outer.style.overflow = "scroll";
        // add innerdiv
        var inner = document.createElement("div");
        inner.style.width = "100%";
        outer.appendChild(inner);
        var widthWithScroll = inner.offsetWidth;
        // remove divs
        outer.parentNode.removeChild(outer);
        return widthNoScroll - widthWithScroll;
    }


    var dict = {
        title: 0,
        type: 0,
        description: 0,
        units: 0,
        id: 0,
        specialType: 0,
        specialTypeDetail: 0
    };

    for(var key in dict) {
        dict[key] = columnHasSomething('td.m-' + key);
    }

    var body = $('#metadata-table > tbody');
    var total_width_to_distribute = 0;
    var columns_to_show = 0;
    var width_used = 0;
    var distribution = 0;
    for(var key in dict) {
        if (dict[key] === 1){
            columns_to_show++;
            width_used = width_used + $("th.m-" + key).outerWidth();
        }
        else{
            total_width_to_distribute = total_width_to_distribute + $("th.m-" + key).outerWidth();
        }
    }
    if (columns_to_show !== Object.keys(dict).length){
        if (body.get(0).scrollHeight > body.height()){
                distribution = (body.width() - getScrollbarWidth() - width_used)/columns_to_show;
        }
        else {
            distribution = (body.width() - width_used)/columns_to_show;
        }
    }

    for(var key in dict) {
        if (dict[key] === 0) {
            $("th.m-" + key).css('display', 'none');
            $("td.m-" + key).css('display', 'none');
        }
    }
    for(var key in dict){
        if (dict[key] === 1){
            $("th.m-" + key).width($("th.m-" + key).width() + distribution);
            $("td.m-" + key).width($("td.m-" + key).width() + distribution);
        }
    }

    if (body.get(0).scrollHeight > body.height()){
        $("td.m-specialTypeDetail").css("padding-right", 0);
        $("td.m-specialTypeDetail").width(parseInt($("td.m-specialTypeDetail").width()) - body.width()*0.01);
        $("td.m-description").width(parseInt($("td.m-description").width()) + body.width()*0.005);
        $("td.m-specialType").width(parseInt($("td.m-specialType").width()) + body.width()*0.005);
    }

});