function showErrorOnField(field, errorText) {
    field.after(createErrorLabel(errorText));
}

function createErrorLabel(text) {
    var newLabel = document.createElement('label');
    newLabel.appendChild(document.createTextNode(text));
    newLabel.className += "input-error";
    return newLabel;
}

function cleanErrorLabels() {
    $('label.input-error').remove();
}