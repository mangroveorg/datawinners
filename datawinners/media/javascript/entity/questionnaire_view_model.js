var questionnaireViewModel =
{
    questions : ko.observableArray([]),
    hasAddedNewQuestions : false,
    qtype : "project",

    addQuestion : function() {
        var question = new DW.question();
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        question.loaded(false);
        var test_code = DW.generateQuestionCode();
        question.code(questionnaireViewModel.check_unique_code(test_code));
        if ($('#qtype') != undefined) {
            var id_question = questionnaireViewModel.questions.pop();
        }
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        if ($('#qtype') != undefined) {
            questionnaireViewModel.questions.push(id_question);
        }
        questionnaireViewModel.questions.valueHasMutated();
        DW.charCount();
        questionnaireViewModel.hasAddedNewQuestions = true;
    },
    loadQuestion: function(question) {
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.questions.valueHasMutated();
    },
    canQuestionBeDeleted: function() {
        return questionnaireViewModel.questions().length > 2;
    },
    removeQuestion: function(question) {
        var index = $.inArray(question, questionnaireViewModel.questions());
        questionnaireViewModel.questions.remove(question);
        if(questionnaireViewModel.questions().length == 0){
            DW.current_code = 1;
            questionnaireViewModel.addQuestion();qtype
            return;
        }
        var next_index = (index) % questionnaireViewModel.questions().length;
        if(index == questionnaireViewModel.questions().length){
            DW.current_code -= 1;
        }
        questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
        questionnaireViewModel.hasAddedNewQuestions = true;
        questionnaireViewModel.reassignQuestionCodes(index);
    },
    removeQuestionCheck:function(question){
        if($('#qtype') != undefined) {
            $("#delete_warning").dialog("open");
            $("#delete_ok").unbind('click').click(function(){
                questionnaireViewModel.removeQuestion(question);
                $("#delete_warning").dialog("close");
            });
            $("#delete_cancel").unbind('click').click(function(){
                $("#delete_warning").dialog("close");
                return false;
            });
        } else {
            var index = $.inArray(question, questionnaireViewModel.questions());
            if ( questionnaireViewModel.questions()[index].event_time_field_flag()){
              $("#delete_question").dialog("open");
            } else {
                questionnaireViewModel.removeQuestion(question)
            }
            $("#ok_button_que_change").bind("click", function(){
                questionnaireViewModel.removeQuestion(question)
                $("#delete_question").dialog("close");
            });
            $("#cancel_link_que").bind("click", function(){
                $("#delete_question").dialog("close");
                return false;
            });
        }
    },
    removeIfQuestionIsSelectedQuestion: function(question) {
        if (questionnaireViewModel.selectedQuestion() == question) {
            questionnaireViewModel.removeQuestion(question);
        }
    },
    showAddChoice:function() {
        if (questionnaireViewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice") {
            if (questionnaireViewModel.selectedQuestion().choices().length == 0) {
                questionnaireViewModel.addOptionToQuestion();
                questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
            }
            return true;
        }
        return false;
    },
    showDateFormats:function() {
        return questionnaireViewModel.selectedQuestion().type() == "date";
    },
    showAddRange:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'integer';
    },
    showAddTextLength:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'text';
    },
    addOptionToQuestion: function() {
        var lastChoice = questionnaireViewModel.selectedQuestion().choices()[questionnaireViewModel.selectedQuestion().choices().length - 1];
        questionnaireViewModel.selectedQuestion().choices.push({text:"", val:String.fromCharCode(lastChoice.val.charCodeAt(0) + 1)});
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeOptionFromQuestion:function(choice) {
        var choices = questionnaireViewModel.selectedQuestion().choices();
        var indexOfChoice = $.inArray(choice, choices);
        var lastChoiceValue = choice['val'].charCodeAt(0);
        var i = indexOfChoice + 1;
        for(i; i < choices.length; i=i+1){
            choices[i]['val'] = String.fromCharCode(lastChoiceValue);
            lastChoiceValue = lastChoiceValue + 1;
        }
        questionnaireViewModel.selectedQuestion().choices.remove(choice);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
    },
    selectedQuestion: ko.observable({}),
    changeSelectedQuestion: function(question) {
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        $(this).addClass("question_selected");
    },
    clearChoices: function() {
        questionnaireViewModel.selectedQuestion().choices([]);
    },
    showLengthLimiter: function() {
        return questionnaireViewModel.selectedQuestion().length_limiter() == 'length_limited';
    },
    check_unique_code: function(test_code) {
        var q;
        for (q in questionnaireViewModel.questions()) {
            if (test_code == questionnaireViewModel.questions()[q].code()) {
                test_code = DW.generateQuestionCode();
                test_code = questionnaireViewModel.check_unique_code(test_code);
                return test_code;
            }
        }
        return test_code;
    },
    choiceCanBeDeleted: function() {
        return questionnaireViewModel.selectedQuestion().choices().length > 1 && questionnaireViewModel.isEnabled();
    },
    isEnabled: function(){
        if($("#not_wizard").length>0){
            return questionnaireViewModel.selectedQuestion().isenabled();
        }
        else{
            return true;
        }
    },
    isTypeEnabled: function(){
        if ($('#qtype') != undefined) {
            return questionnaireViewModel.isEnabled() && !questionnaireViewModel.selectedQuestion().event_time_field_flag() && !questionnaireViewModel.selectedQuestion().loaded();
        } else {
            return questionnaireViewModel.isEnabled() && !questionnaireViewModel.selectedQuestion().event_time_field_flag();
        }
    },
    reassignQuestionCodes:function(index){
        DW.current_code = index+1;
        var new_code = DW.current_code;
        for ( var i=index;i< questionnaireViewModel.questions().length;i++){
            questionnaireViewModel.questions()[i].code(DW.generateQuestionCode());
        }
    },
    setAsRegistration: function() {
        questionnaireViewModel.isRegistration = true;
    }
};