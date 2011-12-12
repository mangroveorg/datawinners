$(document).ready(function() {
    $("#add_subject_type").accordion({collapsible: true,autoHeight:false, active:2});

    $("#add_new_subject_type").live("click", function() {
        $("#type_message").html('');
        $("#type_message").removeClass("message-box");
        $("#add_subject_type_content").removeClass("none");
        $("#id_entity_type_text").val("");
        $("#summary_report").addClass("sum_report");
        $("#individual_report").addClass("ind_report");
        $("#summary_report_tooltip").addClass("sum_report_tooltip");
    });

    function should_append(options, new_type) {
        var i =0;
        for (i; i < options.length; i=i+1) {
            if (new_type == options[i].value){
                return false;
            }
        }
        return true;
    }
    
    $("#add_type").live("click", function() {
        $("#type_message").html("<span class='ajax_loader_small'></span>");
        var new_type = $("#id_entity_type_text").val().toLowerCase();
        $.post("/entity/type/create/", { entity_type_regex: new_type},
                function(response) {
                    var data = JSON.parse(response);
                    if (data.success) {
                        var options = $("#id_entity_type").attr('options');
                        if (should_append(options, new_type)) {
                            $("#id_entity_type").prepend($('<option></option>').val(new_type).html(new_type));
                        }
                        $('#id_entity_type').val(0);
                        $('#id_entity_type').trigger('change');
                        $("#add_subject_type").accordion({collapsible: true,autoHeight:false, active:2});
                        $("#type_message").html('');
                        $("#type_message").removeClass("message-box");
                        $("#id_entity_type_text").val("");
                    }
                    else {
                        $("#type_message").html(data.message);
                        $("#type_message").addClass("message-box");
                    }
                });
    });

    $("#read_more").dialog({
        title: gettext("Read More"),
        modal: true,
        autoOpen: false,
        width: 750
    });

    $('.help_icon').click(function(){
        $("#read_more").dialog("open");
        return false;
    });

});
