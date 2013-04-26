DW.Device = function (deviceElement) {
    this.deviceElement = deviceElement;
    this.disable = function () {
        $(this.deviceElement).attr("disabled", true);
    };
    this.enable = function () {
        $(this.deviceElement).attr("disabled", false);
    };
    this.checked = function () {
        $(this.deviceElement).attr("checked", "checked");
    }
};


var sms_device = new DW.Device("#id_devices_0");

DW.Email = function(emailFieldId, emailHelpTextId, userCreationInfoLabelId, visibilityFactor){
    this.setVisibility = function() {
        if($(visibilityFactor).is(":checked")) show();
        else hide();
    };

    var hide = function(){
        $(emailFieldId).hide();
        $(emailHelpTextId).hide();
        $(userCreationInfoLabelId).hide();
    };

    var show = function(){
        $(emailFieldId).show();
        $(emailHelpTextId).show();
        $(userCreationInfoLabelId).show();
    };
};

var email = new DW.Email("#email_field", "#email_field_help_text", "#user_creation_info", "#id_devices_1");

$(document).ready(function () {
    sms_device.disable();
    email.setVisibility();
    $(document).ajaxStop($.unblockUI);
    $("#id_devices_1").unbind().live('click', function () {
        email.setVisibility();
    });
    $("#id_register_button").unbind().live('click', function () {
        $.blockUI({
            message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
            css:{ width:'275px', top:'400px', left:'800px'}
        });
        $('#id_location').val($.trim($('#id_location').val()));
        $('#id_geo_code').val($.trim($('#id_geo_code').val()));
        $.ajax({
            type:'POST',
            url:sender_registration_link,
            data:$("#registration_form").serialize(),
            success:function (response) {
                $.unblockUI()
                $("#add_data_sender_form").html(response);
                new DW.InitializeEditDataSender().init();
                $("#id_location").catcomplete({
                    source:"/places"});
                sms_device.checked();
                sms_device.disable();
                email.setVisibility();
                $("#generate_id").unbind().click(function() {
                    if($(this).is(":checked")) {
                        $(".subject_field").attr("disabled", "disabled");
                        $(".subject_field").val('');
                    } else {
                        $(".subject_field").removeAttr("disabled");
                    }
                });
                DW.set_focus_on_flash_message();
                if ( $("#cancel_submission_warning_message").length){
                    if (!$("#flash-message.success-message-box").length)
                        DW.edit_datasender.init();
                    else {
                        DW.edit_datasender.init_warning_dialog();
                        $("a[href]").unbind();
                    }
                }
            },
            error:function (e) {
                $("#message-label").show().html("<label class='error_message'>" + e.responseText + "</label>");
                sms_device.checked();
                sms_device.disable();
                email.setVisibility();
                DW.set_focus_on_flash_message();
            }
        });
    });

    $("#id_location").catcomplete({
        source:"/places"
    });

});
