$(function () {

    var hint = $('#log-hint');
    var username = $('#username');
    var password = $('#password');
    var register_username = $('#register-username');
    var register_password = $('#register-password');
    var register_confirm_password = $('#register-confirm-password');

    $('#login-form-link').click(function (e) {
        $("#login-form").delay(100).fadeIn(100);
        $("#register-form").fadeOut(100);
        $('#register-form-link').removeClass('active');
        $(this).addClass('active');
        hint.text("");
        e.preventDefault();
    });
    $('#register-form-link').click(function (e) {
        $("#register-form").delay(100).fadeIn(100);
        $("#login-form").fadeOut(100);
        $('#login-form-link').removeClass('active');
        $(this).addClass('active');
        hint.text("");
        e.preventDefault();
    });

    $('#login-form').submit(function () {
        if (username.val() === "") {
            hint.text("username is empty");
            return false;
        } else if (password.val() === "") {
            hint.text("password is empty");
            return false;
        }
        return true;
    });

    $('#register-form').submit(function () {
        if (register_username.val() === "") {
            hint.text("register username is empty");
            return false;
        } else if (register_password.val() === "") {
            hint.text("register password is empty");
            return false;
        } else if (register_confirm_password.val() === "") {
            hint.text("confirm password is empty");
            return false;
        } else if (register_confirm_password.val() !== register_password.val()) {
            hint.text("confirm password not match");
            return false;
        }
        return true;
    });

});
