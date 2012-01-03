DW.smsPreview = function() {
    var sms_preview = '' + $('#questionnaire-code').val();
    var i = 0;
    for (i; i < viewModel.questions().length; i=i+1) {
        var current_question = viewModel.questions()[i];
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                sms_preview +=  ' '+gettext('number');
                break;
            case 'text':
                sms_preview +=  ' '+gettext('text');
                break;

            case 'date':
                sms_preview += ' date';
                break;

            case 'select':
                sms_preview += ' '+gettext('list of choices');
                break;

            case 'select1':
                sms_preview += ' '+gettext('list of choices');
                break;

            case 'geocode':
                sms_preview += ' ' + gettext('geo code');
                break;
        }
    }
    $('#sms_preview').html(sms_preview);
};
