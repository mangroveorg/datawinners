$(document).ready(function() {
    if (!$(".subject_field").val()) {
        $(".subject_field").attr("disabled", "disabled");
    } else {
        $("#generate_id").attr("checked", false);
        $(".subject_field").removeAttr("disabled");
    }
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

    if ( $("#cancel_submission_warning_message").length ){
        DW.bind_project_links = function() {
            return;
        }
        DW.edit_datasender = new DW.data_submission({});
    }

    $('.secondary_tab li:first-child').attr('class', 'inactive');
    $('.secondary_tab li:nth-child(2)').attr('class', 'active');

});