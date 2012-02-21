DW.smsPreview = function() {
    $('#sms_preview').html($('#questionnaire-code').val());
    $.each(questionnaireViewModel.questions(), function(index){
        $('#sms_preview').append(' '+gettext('answer')+(index+1));
    });
};
