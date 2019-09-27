var securePassword = function (password) {
    if (!ckanextSecurityActivated()) {
        return password.length >= 4;
    }

    if (password.length < 10) {
        return false;
    }

    var hasLowercase = /[a-z]+/.test(password);
    var hasUppercase = /[A-Z]+/.test(password);
    var hasNumber = /[0-9]+/.test(password);
    var hasSymbol = /[^a-zA-Z0-9 :]+/.test(password);
    var amountTrue = hasLowercase + hasUppercase + hasNumber + hasSymbol;
    return amountTrue >= 3;
};


var ckanextSecurityActivated = function () {
    return $("#token-generator input").val() !== undefined
};


var insecurePasswordMessage = function (input) {
    if (ckanextSecurityActivated()) {
        showNegativeFeedback(input, "La contraseña ingresada no es segura. Debe tener al menos diez caracteres, y al menos 3 de los siguientes caracteres: una letra minúscula, una letra mayúscula, un número, o un símbolo");
    } else {
        showNegativeFeedback(input, "La contraseña ingresada no es segura. Debe tener al menos 4 caracteres.");
    }
};