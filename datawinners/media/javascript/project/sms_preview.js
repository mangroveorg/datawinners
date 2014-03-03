DW.smsPreview = function() {
    $('#sms_preview').html(questionnaireViewModel.questionnaireCode());
    $.each(questionnaireViewModel.questions(), function(index){
        $('#sms_preview').append(' '+gettext('answer')+(index+1));
    });
};
