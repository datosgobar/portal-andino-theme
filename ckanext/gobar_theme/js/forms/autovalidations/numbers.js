function valueIsPositiveNumber(value) {
    return +value > 0;
}

function valueIsPositiveInteger(value) {
    return (valueIsPositiveNumber(value) || +value === 0);
}