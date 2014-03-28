DW.questionnaire_tab_get_post_data = function(){
    return {'questionnaire-code':$('#questionnaire-code').val(),
        'question-set':JSON.stringify(ko.toJS(questionnaireViewModel.questions())),
        'project_id': $("#project-id").val(),
        'project_state': 'Active'
    };
};

DW.web_instruction_and_preview.prototype.get_post_data = DW.questionnaire_tab_get_post_data;
DW.sms_instruction_and_preview.prototype.get_post_data = DW.questionnaire_tab_get_post_data;

DW.questionnaire_form_validate = function(){
    return $('#question_form').valid();
};

$(function(){
    var sms_preview = new DW.sms_instruction_and_preview();
    sms_preview.bind_preview_navigation_item();
    var web_preview = new DW.web_instruction_and_preview();
    web_preview.bind_preview_navigation_item();
    var web_preview = new DW.smart_phone_instruction_and_preview();
    web_preview.bind_preview_navigation_item();
});
