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

    if($('#id_frequency_period').val() == ''){
        $('#has_deadline_block').hide();
        $('#deadline_day_block').hide();
        $('#deadline_type_block').hide();

    }
    if($('#id_has_deadline_1').is(':checked')){
        $('#deadline_day_block').hide();
        $('#deadline_type_block').hide();
    }
    
    $('#span_deadline_type').html($('#id_frequency_period').val());
    $('#id_frequency_period').change(function(element){
        if ($('#id_frequency_period').val() != ''){
            $('#has_deadline_block').show();
            $('#deadline_day_block').show();
            $('#deadline_type_block').show();
        }else{
            $('#has_deadline_block').hide();
            $('#deadline_day_block').hide();
            $('#deadline_type_block').hide();
            return;
        }
//        if ($('#id_frequency_period').val() != '') {
//            options = _.range(1, 32).map(function(n) {
//                return new Option(n, n)
//            })
//            $("#id_deadline_day").append(options);
//        }
        $('#span_deadline_type').html($('#id_frequency_period').val());
        $('input[name="has_deadline"]').change(function(){
            if($('#id_has_deadline_1:checked').length > 0){
                $('#deadline_day_block').hide();
                $('#deadline_type_block').hide();
            }else{
                $('#deadline_day_block').show();
                $('#deadline_type_block').show();
            }
        });
    });
});
    