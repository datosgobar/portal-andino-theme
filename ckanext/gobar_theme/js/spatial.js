$(document).ready(function () {
    var ARGENTINA_CODE = 'ARG';

    var toggleSpatialSelects = function(countryCode) {
        if (ARGENTINA_CODE != countryCode) {
            $("#province-field").val('');
            $("#district-field").val('');

            $('.internal').hide();
        } else {
            $('.internal').show();
        }
    }

    $.ajax({
        url: '/spatial/paises',
    }).done(function(data) {
        var select = $("#country-field");
        var currentValue = select.val();

        toggleSpatialSelects(currentValue);

        var countries = {};

        countries.results = $.map(data.paises, function (obj) {
            obj.id = obj.id || obj.code;
            obj.text = obj.text || obj.common_name;
            obj.selected = currentValue == obj.code

            return obj;
        });

        select.select2({
            placeholder: 'Seleccione un país',
            allowClear: true,
            data: countries
        });

        select.on('change', function(e) {
            var countryCode = null;
            if (e.added && e.added.id) {
                countryCode = e.added.id;
            }
            $("#province-field").val('');
            toggleSpatialSelects(countryCode);
        });
    });

    $.ajax({
        url: '/spatial/provincias',
    }).done(function(data) {
        var select = $("#province-field");
        var currentValue = select.val();
        var provinces = {};

        provinces.results = $.map(data.provincias, function (obj) {
            obj.text = obj.text || obj.nombre;
            obj.selected = currentValue == obj.code

            return obj;
        });

        select.select2({
            placeholder: 'Seleccione una provincia',
            allowClear: true,
            data: provinces
        });
    });
    
    var provinceSelect = $("#province-field");
    var selectedProvince = provinceSelect.val();

    var initDistrictSelect = function(selectedProvince) {
        $.ajax({
            url: '/spatial/municipios?provincia_id=' + selectedProvince,
        }).done(function(data) {
            var select = $("#district-field");
            var currentValue = select.val();
            var districts = {};
    
            districts.results = $.map(data.municipios, function (obj) {
                obj.text = obj.text || obj.nombre;
                obj.selected = currentValue == obj.code
    
                return obj;
            });
    
            select.select2({
                placeholder: 'Seleccione un distrito',
                allowClear: true,
                multiple: true,
                data: districts
            });
        });
    }

    initDistrictSelect(selectedProvince);

    provinceSelect.on('change', function (e) {
        var selectedProvince = null;
        if (e.added) {
            selectedProvince = e.added.id;
        }
        $("#district-field").val('');
        initDistrictSelect(selectedProvince);
    });
});
