$(document).on("click", "#id_register_button", function () {
    $.blockUI({
        message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
        css: { width: '275px', top: '400px', left: '800px', zIndex: 1000000}
    });
    $('#id_location').val($.trim($('#id_location').val()));
    $('#id_geo_code').val($.trim($('#id_geo_code').val()));
    $.ajax({
        type: 'POST',
        url: sender_registration_link || window.location.href,
        data: $("#registration_form").serialize(),
        success: function (response) {
            $.unblockUI();
            $("#add_data_sender_form").html(response);
            $("#id_location").catcomplete({
                source: "/places"});
            reporter_id_generation_action();
            updateShortCodeDisabledState();
            DW.set_focus_on_flash_message();
            new DW.InitializeEditDataSender().init();
        },
        error: function (e) {
            $.unblockUI();
            $("#message-label").show().html("<label class='error_message'>" + e.responseText + "</label>");
            DW.set_focus_on_flash_message();
        }
    });
});

$(document).ready(function () {
    $(document).ajaxStop($.unblockUI);
    $("#id_location").catcomplete({
        source: "/places"
    });
    new DW.UniqueIdField("#registration_form");
});

function updateShortCodeDisabledState(){
    if ($("#id_generated_id").is(":checked")) {
        $(".subject_field").attr("disabled", "disabled");
        $(".subject_field").val('');
    } else {
        $(".subject_field").removeAttr("disabled");
    }
}

function reporter_id_generation_action() {
    $("#id_generated_id").on('click', function () {
        if ($(this).is(":checked")) {
            $(".subject_field").attr("disabled", "disabled");
            $(".subject_field").val('');
        } else {
            $(".subject_field").removeAttr("disabled");
        }
    });
}
