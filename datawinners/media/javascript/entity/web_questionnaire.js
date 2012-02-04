$(document).ready(function() {
    $(".subject_field").attr("disabled", "disabled");
    $("#generate_id").click(function() {
        if($(this).is(":checked")) {
            $(".subject_field").attr("disabled", "disabled");
            $(".subject_field").val('');
        } else {
            $(".subject_field").removeAttr("disabled");
        }
    });

    $(".location_field").catcomplete({
        source: "/places"
    });

});