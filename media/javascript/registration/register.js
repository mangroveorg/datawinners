$(document).ready(function() {
    $('#submit_registration_form').bind("click", function() {
        $('#submit_registration_form').attr("disabled", true);
        $('#registration_form').submit();
    });
});