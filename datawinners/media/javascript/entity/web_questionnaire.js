$(document).ready(function() {
    $("#id_s").attr("disabled", "disabled");
    $("#generate_id").click(function() {
        if($(this).is(":checked")) {
            $("#id_s").attr("disabled", "disabled");
            $("#id_s").val('');
        } else {
            $("#id_s").removeAttr("disabled");
        }
    });
});