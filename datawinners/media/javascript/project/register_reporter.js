$(document).ready(function() {
    $(document).ajaxStop($.unblockUI);
    $("#id_register_button").unbind().live('click', function() {
        $.blockUI({
            message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
            css: { width:'275px',top: '400px', left: '800px'}
        });
        $.ajax({
            type: 'POST',
            url: sender_registration_link,
            data: $("#registration_form").serialize(),
            success:function(response) {
                $("#add_data_sender_form").html(response);
                $("#id_location").catcomplete({
                    source: "/places"});
            },
            error: function(e) {
                $("#message-label").show().html("<label class='error_message'>" + e.responseText + "</label>");
            }

        });
    });

    $("#id_location").catcomplete({
        source: "/places"
    });

});
