DW.smsPreview = function() {
    var sms_preview = '' + $('#questionnaire-code').val();
    var i = 0;
    for (i; i < questionnaireViewModel.questions().length; i=i+1) {
        var current_question = questionnaireViewModel.questions()[i];
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                sms_preview +=  ' '+gettext('number');
                break;
            case 'text':
                sms_preview +=  ' '+gettext('word');
                break;

            case 'date':
                sms_preview += ' date';
                break;

            case 'select':
                sms_preview += ' '+gettext('choice(s)');
                break;

            case 'select1':
                sms_preview += ' '+gettext('choice');
                break;

            case 'geocode':
                sms_preview += ' ' + gettext('GPS');
                break;
        }
    }
    $('#sms_preview').html(sms_preview);
};
