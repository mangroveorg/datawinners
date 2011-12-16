DW.smsPreview = function() {
    var sms_preview = '' + $('#questionnaire-code').val();
    var i = 0;
    for (i; i < viewModel.questions().length; i=i+1) {
        var current_question = viewModel.questions()[i];
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                sms_preview += ' &lt;' + gettext('number') + '&gt;';
                break;
            case 'text':
                sms_preview += ' &lt;' + gettext('text') + '&gt;';
                break;

            case 'date':
                sms_preview += ' &lt;date&gt;';
                break;

            case 'select':
                sms_preview += ' &lt;' + gettext('list of choices') + '&gt;';
                break;

            case 'select1':
                sms_preview += ' &lt;' + gettext('list of choices') + '&gt;';
                break;

            case 'geocode':
                sms_preview += ' &lt;' + gettext('geo code') + '&gt;';
                break;
        }
    }
    $('#sms_preview').html(sms_preview);
};
