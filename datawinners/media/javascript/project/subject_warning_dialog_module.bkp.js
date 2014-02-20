DW.change_description = function(){
    $(questionnaireViewModel.questions()).each(function (question) {
        var question_title = this.title();
        if (this.is_entity_question()) {
            var subject_name = gettext("subject");
            this.title(question_title.replace(subject_name, $('#id_entity_type').val()));
        }
      });
    questionnaireViewModel.questions.valueHasMutated();
}

DW.continue_flip = function(){
    DW.subject_warning_dialog_module.enable_or_disable_entity_type_control();
    if (DW.subject_warning_dialog_module.is_subject_selected()) {
        DW.init_view_model(subject_report_questions);
        DW.change_description();
        basic_project_info.show_subject_link();
    }
    else {
        DW.init_view_model(activity_report_questions);
        basic_project_info.hide_subject_link();
    }
    DW.current_subject = $('#id_entity_type').val();
    DW.current_project_selected = DW.subject_warning_dialog_module.get_selected_project();
    return false;
};

DW.subject_warning_dialog_module={
    init: function(){
        DW.ACTIVITY_REPORT_PROJECT=1;
        DW.SUBJECT_PROJECT=2;
        DW.current_subject = $('#id_entity_type').val();
        DW.current_project_selected= DW.subject_warning_dialog_module.get_selected_project();
        DW.subject_warning_dialog_module.init_subject_warning_dialog();
        DW.subject_warning_dialog_module.bind_dialog_closed();
        DW.subject_warning_dialog_module.bind_cancel_link();
        DW.subject_warning_dialog_module.bind_continue();
        DW.subject_warning_dialog_module.enable_or_disable_entity_type_control();
    },


    init_subject_warning_dialog:function(){
        var width = gettext("en") == "en" ? 400 : 420;
        $("#subject_warning_message").dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: false,
            height: 225,
            width: width,
            closeText: 'hide'
        });
    },

    bind_dialog_closed:function(){
        $( "#subject_warning_message" ).bind( "dialogclose", function(event, ui) {
            $('#id_entity_type').val(DW.current_subject);
            if(DW.current_project_selected!=DW.subject_warning_dialog_module.get_selected_project()){
               DW.subject_warning_dialog_module.handle_subject_warning_cancel();
            }
        });
        return false;

    },
    bind_cancel_link:function(){
        $(".cancel_link").bind("click", function(){
            DW.subject_warning_dialog_module.handle_subject_warning_cancel();
            $("#subject_warning_message").dialog("close");

        });

    },

    bind_continue:function(){
        $("#continue").bind("click", function(){
            DW.continue_flip();
            $("#subject_warning_message").dialog("close");
        });
    },

    enable_or_disable_entity_type_control:function(){
        if (DW.subject_warning_dialog_module.is_subject_selected()) {
            $('#id_entity_type').attr('disabled', false);
        }
        else {
            $('#id_entity_type').attr('disabled', true);
        }
    },

    is_activity_report_selected:function(){
        return $('input[name="activity_report"]:checked').val() == "yes";
    },
    is_subject_selected:function(){
        return !DW.subject_warning_dialog_module.is_activity_report_selected();
    },
    get_selected_project:function(){
        if (DW.subject_warning_dialog_module.is_activity_report_selected()){
            return DW.ACTIVITY_REPORT_PROJECT;
        }
        return DW.SUBJECT_PROJECT;

    },
    handle_subject_warning_cancel:function(){
        if(DW.current_project_selected==DW.ACTIVITY_REPORT_PROJECT){
            $('#id_activity_report_0').attr("checked", true);
        }
        else{
            $('#id_activity_report_1').attr("checked", true);

        }

    }

};
