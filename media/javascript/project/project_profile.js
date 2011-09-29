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
        title: gettext("Warning !!"),
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

    deadline_init();
    $($('input[name="frequency_enabled"]')).change(function(){
        toggle_deadline_block();
        toggle_frequency_period();
    });

    $($('input[name="has_deadline"]')).change(function(){
        toggle_has_deadline();
    });

    $('#id_frequency_period').change(function(){
        enable_timeperiod();
    });

    $('#id_deadline_week,#id_deadline_month,#id_deadline_type,#id_frequency_period').change(function(){
        DW.set_deadline_example();
    });

    DW.set_deadline_example = function(e){
        var frequency = $('#id_frequency_period').val();

        if (frequency == 'week'){
            var deadline_example =  $('#id_deadline_week option:selected').text() + ' of '+$('#id_deadline_type:not(:disabled) option:selected').text()+ ' week';
        }else if (frequency == 'month')
        {
            var deadline_example = $('#id_deadline_month option:selected').text() + ' of January'
        }
        $('#deadline_example').text(deadline_example)
    }

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
        $('#week_block :input').attr('disabled', false);
        $('#month_block :input').attr('disabled', true);
    } else if ($('#id_frequency_period').val() == "month") {
        $('#week_block :input').attr('disabled', true);
        $('#month_block :input').attr('disabled', false);
        show_element($('#week_block'), "False")
        show_element($('#month_block'), "True")
    }
}

function toggle_has_deadline() {
    if ($('input[name="has_deadline"]:checked').val() == "True") {
        show_element($('#time_period'), "True");
        $('#time_period :input').attr('disabled', false);
        enable_timeperiod()
    } else {
        $('#time_period :input').attr('disabled', true);
        show_element($('#time_period'), "False");
    }
}


function deadline_init() {
    show_element($('#deadline_block'), $('input[name="frequency_enabled"]:checked').val());
    toggle_frequency_period();
}

function toggle_frequency_period(){
    if ($('input[name="frequency_enabled"]:checked').val() == "True") {
        $('#id_frequency_period').attr('disabled', false);
    }else{
        $('#id_frequency_period').attr('disabled', true);

        $('input[name="has_deadline"]').attr('disabled', true);
    }
    toggle_has_deadline();
}

function toggle_deadline_block(){
    show_element($('#deadline_block'), $('input[name="frequency_enabled"]:checked').val())
    if($('input[name="frequency_enabled"]:checked').val() == "True"){
        $('input[name="has_deadline"]').attr('disabled', false);
    }else{
        $('input[name="has_deadline"]').attr('disabled', true);
    }
}
