var securePassword = function (password) {
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
