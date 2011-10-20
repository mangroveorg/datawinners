DW.smsPreview = function() {
    var sms_preview = '' + $('#questionnaire-code').val()
    for (var i = 0; i < viewModel.questions().length; i++) {
        var current_question = viewModel.questions()[i];
        if (!use_ordered_sms_parser){
            sms_preview += ' .'+current_question.code()
        }
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                sms_preview += ' &lt;number&gt;'
                break;
            case 'text':
                sms_preview += ' &lt;text&gt;'
                break;

            case 'date':
                sms_preview += ' &lt;date&gt;'
                break;

            case 'select':
                sms_preview += ' &lt;list of choices&gt;'
                break;

            case 'select1':
                sms_preview += ' &lt;list of choices&gt;'
                break;

            case 'geocode':
                sms_preview += ' &lt;geo code&gt;'
        }
    }

    $('#sms_preview').html(sms_preview);
};