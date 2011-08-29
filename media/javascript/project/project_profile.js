$(document).ready(function(){
    if ($('#id_activity_report_0').attr('checked')==true) {
             $('#id_entity_type').attr('disabled', true);
        DW.current_activity_report = $('#id_activity_report_0').val();
    }
    else{
         DW.current_activity_report = $('#id_activity_report_1').val();
    }
    DW.current_type = $('#id_entity_type').val();

    $("#tab_items .define").addClass("current");
    set_current_tab();
    $("#id_devices_0").attr('disabled', true);

    $('#submit-button').click(function(){
       $('#id_devices_0').attr('disabled',false);
       $('#profile_form').submit();
    });


    $("#id_activity_report_0").live("click", function(){
        $("#id_entity_type").attr("disabled", true);
        DW.open_activity_report_warning();
    });
    $("#id_activity_report_1").live("click", function(){
        $("#id_entity_type").attr("disabled", false);
        DW.open_activity_report_warning();
    })
    $("#profile_warning_message").dialog({
        title: "Warning !!",
        modal: true,
        autoOpen: false,
        height: 200,
        width: 300,
        closeText: 'hide'
      }
  );

    $("#id_entity_type").change(function(){
        $("#profile_warning_message").dialog("open");
    });
    $(".cancel_link").bind("click", function(){
        $('#id_entity_type').val(DW.current_type);
        $.each($("input[name=activity_report]"), function(){
            if ($(this).val()== DW.current_activity_report){
                $(this).attr("checked",true);
            }
        });
        $("#profile_warning_message").dialog("close");
    });
    $("#continue").bind("click", function(){
        $("#profile_warning_message").dialog("close");
    });

    DW.open_activity_report_warning = function(){
        $("#profile_warning_message").dialog("open");
    }

    //Based on has_frequency orchestrate the month/week blocks.
    show_element($('#deadline_block'),$('input[name="frequency_enabled"]:checked').val());
    enable_timeperiod();
    toggle_has_deadline();
    $($('input[name="frequency_enabled"]')).change(function(){
        show_element($('#deadline_block'), $('input[name="frequency_enabled"]:checked').val())
    });

    $($('input[name="has_deadline"]')).change(function(){
        toggle_has_deadline();
    });

    $('#id_frequency_period').change(function(){
        enable_timeperiod();
    });

});

function show_element(element,should_show){
    if(should_show=='True'){
        $(element).show();
    }else{
        $(element).hide();
    }

}


function enable_timeperiod() {
    if ($('#id_frequency_period').val() == "week") {
        show_element($('#week_block'), "True")
        show_element($('#month_block'), "False")
    } else if ($('#id_frequency_period').val() == "month") {
        show_element($('#week_block'), "False")
        show_element($('#month_block'), "True")
    }
}

function toggle_has_deadline() {
    if ($('input[name="has_deadline"]:checked').val() == "True") {
        show_element($('#time_period'), "True");
        enable_timeperiod()
    } else {
        show_element($('#time_period'), "False");
    }
}
