$(document).ready(function(){
    $("#id_entity_type_text").live("blur", function(){
        $("#type_message").html("<span class='ajax_loader_small'></span>");
        var new_type = $("#id_entity_type_text").val().toLowerCase();
        $.post("/entity/type/create/", { entity_type_regex: new_type, default_form_model: false},
                function(response) {
                    var data = JSON.parse(response);
                    if (data.success) {
                        $("#questionnaire-code").val(data.form_code);
                        $("#saved-questionnaire-code").val(data.form_code);
                        $("#saved-questionnaire-code, #id_entity_type_text").attr("disabled", "disabled");
                    }
                    else {
                        $("#type_message").html(data.message);
                        $("#type_message").addClass("message-box");
                    }
            });
    });
});