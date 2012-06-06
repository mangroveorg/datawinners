DW.instruction_and_preview = {
    init: function(){
        DW.instruction_and_preview.bind_sms_preview();
    },

    bind_sms_preview: function(){
        $(".navigation-sms-preview").live('click', DW.instruction_and_preview.sms_preview);
    },

    sms_preview: function () {
        if(DW.questionnaire_form_validate()){
            var post_data = DW.instruction_and_preview.post_data();
            DW.instruction_and_preview.load_preview_content(sms_preview_link, post_data);
        }
        return;
    },

    post_data: function() {
        var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()), null, 2);
        return {'questionnaire-code':$('#questionnaire-code').val(),
            'question-set':questionnaire_data,
            'profile_form':basic_project_info.values()};
    },

    load_preview_content: function(preview_link, post_data) {
        $.post(preview_link, post_data, function(response_data){
            $("#questionnaire_content").html(response_data)
            $("#questionnaire_preview_instruction").show();
        }, 'html')
    }

};


$(function () {
    DW.instruction_and_preview.init();
});