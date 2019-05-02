#!coding=utf-8

def update_frequencies(freq_id=None):
    frequencies = [
        ("R/PT1S", u"Continuamente actualizado"),
        ("R/PT1H", u"Cada hora"),
        ("R/P1D", u"Diariamente"),
        ("R/P0.33W", u"Tres veces a la semana"),
        ("R/P0.5W", u"Dos veces a la semana"),
        ("R/P3.5D", u"Cada media semana"),
        ("R/P1W", u"Semanalmente"),
        ("R/P0.33M", u"Tres veces por mes"),
        ("R/P0.5M", u"Cada 15 días"),
        ("R/P1M", u"Mensualmente"),
        ("R/P2M", u"Bimestralmente"),
        ("R/P3M", u"Trimestralmente"),
        ("R/P4M", u"Cuatrimestralmente"),
        ("R/P6M", u"Cada medio año"),
        ("R/P1Y", u"Anualmente"),
        ("R/P2Y", u"Cada dos años"),
        ("R/P3Y", u"Cada tres años"),
        ("R/P4Y", u"Cada cuatro años"),
        ("R/P10Y", u"Cada diez años"),
        ('eventual', u'Eventual')
    ]
    if freq_id is not None:
        filtered_freq = [freq for freq in frequencies if freq[0] == freq_id]
        if filtered_freq:
            return filtered_freq[0]
        return None
    return frequencies


def field_types(field_type_id=None):
    types = [
        ("string", u"Texto (string)"),
        ("integer", u"Número entero (integer)"),
        ("number", u"Número decimal (number)"),
        ("boolean", u"Verdadero/falso (boolean)"),
        ("time", u"Tiempo ISO-8601 (time)"),
        ("date", u"Fecha ISO-8601 (date)"),
        ("date-time", u"Fecha y hora ISO-8601 (date-time)"),
        ("object", u"JSON (object)"),
        ("geojson", u"GeoJSON (geojson)"),
        ("geo_point", u"GeoPoint (geo_point)"),
        ("array", u"Lista de valores en formato JSON (array)"),
        ("binary", u"Valor binario en base64 (binary)"),
        ("any", u"Otro (any)")
    ]

    if field_type_id:
        filtered_field_type = [t for t in types if t[0] == field_type_id]
        if filtered_field_type:
            return filtered_field_type[0]
        return None

    return types


def distribution_types(distribution_type_id=None):
    types = [
        ("file", u"Archivo de datos"),
        ("api", u"API"),
        ("code", u"Código"),
        ("documentation", u"Documentación")
    ]

    if distribution_type_id:
        filtered_distribution_type = [t for t in types if t[0] == distribution_type_id]
        if filtered_distribution_type:
            return filtered_distribution_type[0]
        return None

    return types


def special_field_types(special_field_type_id=None):
    types = [
        ("time_index", u"Índice de tiempo"),
    ]
    if special_field_type_id is not None:
        filtered_special_field_type = [_id for _id in types if _id[0] == special_field_type_id]
        if filtered_special_field_type:
            return filtered_special_field_type[0]
        return None
    return types


def type_is_numeric(field_type):
    return field_type in ['integer', 'number']