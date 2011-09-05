DW.smsPreview = function() {
    var sms_preview = '' + $('#questionnaire-code').val()
    for (var i = 0; i < viewModel.questions().length; i++) {
        var current_question = viewModel.questions()[i];
        sms_preview += ' +'+current_question.code()
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                sms_preview += ' &ltnumber&gt'
                break;
            case 'text':
                sms_preview += ' &lttext&gt'
                break;

            case 'date':
                sms_preview += ' &ltdate&gt'
                break;

            case 'select':
                sms_preview += ' &ltlist of choices&gt'
                break;

            case 'select1':
                sms_preview += ' &ltlist of choices&gt'
                break;

            case 'geocode':
                sms_preview += ' &ltgeo code&gt'
        }
    }

    $('#sms_preview').html(sms_preview);

};