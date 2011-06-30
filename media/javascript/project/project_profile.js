$(document).ready(function(){
    $("#tab_items .define").addClass("current");
    set_current_tab();
    if ($('#id_activity_report_0').attr('checked')==true) {
             $('#id_entity_type').attr('disabled', true);
    }

    $("#id_activity_report_0").live("click", function(){
        $("#id_entity_type").attr("disabled", true);
    });
    $("#id_activity_report_1").live("click", function(){
        $("#id_entity_type").attr("disabled", false);
    })
});