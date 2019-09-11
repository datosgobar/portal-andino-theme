$(function () {

    $('a#embeber').on('click', function () {
        var id = $('a#embeber').data('module-resource-id');
         $.ajax({
            url: '/dataset/resource_view_embed/' + id,
            type: 'POST'
        });
    });

    var getScrollbarWidth = function () {
        /**
         * Calcula el ancho de una scrollbar en distintos navegadores
         */
        if (!getScrollbarWidth.value) {
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

            getScrollbarWidth.value = widthNoScroll - widthWithScroll;
        }

        return getScrollbarWidth.value;
    };

    var columnHasAnyValue = function (cellSelector) {
        /**
         * Itera por todas las celdas que matcheen el selector.
         * Devuelve un valor booleano que indica si alguna tiene algún valor.
         */
        var hasAnyValue = false;
        $(cellSelector).each(function(index) {
            if ($(this).text().trim().length > 0) {
                hasAnyValue = true;
                return;
            }
        });
        return hasAnyValue;
    };

    var redrawAttributesTable = function () {
        var tableColumns = {
            title: {
                initialPercentage: .13,
                finalPercentage: .13,
                visible: true
            },
            type: {
                initialPercentage: .07,
                finalPercentage: .07,
                visible: true
            },
            description: {
                initialPercentage: .33,
                finalPercentage: .33,
                visible: true
            },
            units: {
                initialPercentage: .16,
                finalPercentage: .16,
                visible: true
            },
            id: {
                initialPercentage: .17,
                finalPercentage: .17,
                visible: true
            },
            specialType: {
                initialPercentage: .07,
                finalPercentage: .07,
                visible: true
            },
            specialTypeDetail: {
                initialPercentage: .07,
                finalPercentage: .07,
                visible: true
            }
        }

        var tableBody = $('#metadata-table > tbody');
        var columnsWithValues = 0;
        var percentageToDistribute = 0;
    
        for(var columnName in tableColumns) {
            tableColumns[columnName].visible = columnHasAnyValue('td.m-' + columnName);

            if (tableColumns[columnName].visible) {
                columnsWithValues++;
            } else {
                percentageToDistribute += tableColumns[columnName].initialPercentage;
                tableColumns[columnName].finalPercentage = 0;
            }
        }

        if (tableBody.get(0) && tableBody.get(0).scrollHeight > tableBody.height()) {
            // Hay un scroll, ajusto las últimas dos columnas
            $("#metadata-table th:nth-last-child(-n+2)").css('padding-right', '4%');
        }

        percentageToDistribute = percentageToDistribute / columnsWithValues;
        for(var columnName in tableColumns) {
            if (tableColumns[columnName].visible) {
                // Reparto el ancho disponible a las columnas visibles
                tableColumns[columnName].finalPercentage += percentageToDistribute;
                $("th.m-" + columnName).css("width", "" + (tableColumns[columnName].finalPercentage * 100) + "%");
                $("td.m-" + columnName).css("width", "" + (tableColumns[columnName].finalPercentage * 100) + "%");
            } else {
                $("th.m-" + columnName).css("display", "none");
                $("td.m-" + columnName).css("display", "none");
            }
        }

        $('#metadata-table').show();
    };

    redrawAttributesTable();

    $( window ).resize(function() {
        redrawAttributesTable();
    });

    $("a.m-id").each(function() {
        var element = $(this);
        var href = element.attr('href');
        $.ajax({
            type: "HEAD",
            async: true,
            url: href,
            timeout: 3000,
            success: function() {
                element.attr('href', href.substring(href.indexOf('/series/api')))
            },
            error: function () {
                console.log("No se encontró la serie en la URL: " + href);
                element.replaceWith(element.text());
            }
        });
    });

});
