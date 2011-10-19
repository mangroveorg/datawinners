DW.smsPreview = function() {
    var sms_preview = '' + $('#questionnaire-code').val()
    for (var i = 0; i < viewModel.questions().length; i++) {
        var current_question = viewModel.questions()[i];
        sms_preview += ' .'+current_question.code()
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                sms_preview += gettext(' &lt;number&gt;')
                break;
            case 'text':
                sms_preview += gettext(' &lt;text&gt;')
                break;

            case 'date':
                sms_preview += ' &lt;date&gt;'
                break;

            case 'select':
                sms_preview += gettext(' &lt;list of choices&gt;')
                break;

            case 'select1':
                sms_preview += gettext(' &lt;list of choices&gt;')
                break;

            case 'geocode':
                sms_preview += gettext(' &lt;geo code&gt;')
        }
    }

    $('#sms_preview').html(sms_preview);

};
