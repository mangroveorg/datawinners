DW.charCount = function() {
    var questionnaireCode = questionnaireViewModel.questionnaireCode();
    var questionnaire_code_len = questionnaireCode ? questionnaireCode.length : 0;
    var max_len = 160;
    var constraints_len = 0;
    var delimiter_len = 1;
    var sms_number = 1;
    var sms_number_text = "";
    var i = 0;
    for (i; i < questionnaireViewModel.questions().length; i=i+1) {
        var current_question = questionnaireViewModel.questions()[i];
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                if (current_question.range_max()){
                    constraints_len = constraints_len + current_question.range_max().toString().length;
                    break;
                }
                if (current_question.range_min()){
                    constraints_len = constraints_len + current_question.range_min().toString().length;
                }
                break;
            case 'text':
                if (current_question.max_length()) {
                    constraints_len = constraints_len + parseInt(current_question.max_length());
                }
                break;
            case 'date':
                constraints_len = constraints_len + current_question.date_format().length;
                break;
            case 'select':
                constraints_len = constraints_len + current_question.choices().length;
                break;
            case 'select1':
                constraints_len = constraints_len + 1;
                break;
        }
        constraints_len = constraints_len + delimiter_len;
    }
    var current_len = questionnaire_code_len + constraints_len;
    if (current_len <= max_len) {
        $("#char-count").css("color", "#666666");
    }
    if (current_len > max_len) {
        $("#char-count").css("color", "red");
        max_len = max_len+160;
        sms_number = sms_number+1;
        sms_number_text = "(" + sms_number + " sms required)";
    }
    $('#char-count').html((current_len) + ' / ' + max_len + ' ' + gettext('characters used') + sms_number_text);

};
