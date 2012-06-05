DW.instruction_and_preview = {
    init: function(){
        DW.instruction_and_preview.bind_sms_preview();
    },

    bind_sms_preview: function(){
        $(".navigation-sms-preview").live('click', DW.instruction_and_preview.sms_preview);
    },

    sms_preview: function () {
        $("#questionnaire_content").load(sms_preview_link, function(){
            $("#questionnaire_preview_instruction").show();
        });
    }
};


$(function () {
    DW.instruction_and_preview.init();
});