var questionnaireViewModel =
{
    questions : ko.observableArray([]),
    hasAddedNewQuestions : false,
    hasDeletedOldQuestion : false,
    language:'en',

    addQuestion : function() {
        var question = new DW.question();
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        question.newly_added_question(true);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
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
    renumberQuestions: function(){
        var questionPattern = /^Question \d+$/;
        for (var i = 0; i < questionnaireViewModel.questions().length; i++){
            var question = questionnaireViewModel.questions()[i];
            if (questionPattern.test(question.title()) )
                question.title("Question " + (i + 1));
        }
    },
    removeQuestion: function(question) {
        var index = $.inArray(question, questionnaireViewModel.questions());
        if (!question.newly_added_question()) {
            questionnaireViewModel.hasDeletedOldQuestion = true;
        }
        questionnaireViewModel.questions.remove(question);
        if(questionnaireViewModel.questions().length == 0){
            questionnaireViewModel.addQuestion();
            return;
        }
        questionnaireViewModel.renumberQuestions();
        var next_index = (index) % questionnaireViewModel.questions().length;
        questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
        questionnaireViewModel.hasAddedNewQuestions = true;
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
        var selectedQuestionCode = "a";
        if (questionnaireViewModel.selectedQuestion().choices().length > 0) {
            var lastChoice = questionnaireViewModel.selectedQuestion().choices()[questionnaireViewModel.selectedQuestion().choices().length - 1];
            selectedQuestionCode = DW.next_option_value(lastChoice.val);
        }
        questionnaireViewModel.selectedQuestion().choices.push({text:"", val:selectedQuestionCode});
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeOptionFromQuestion:function(choice) {
        var choices = questionnaireViewModel.selectedQuestion().choices();
        var indexOfChoice = $.inArray(choice, choices);
        var lastChoiceValue = choice['val'];//.charCodeAt(0);
        var i = indexOfChoice + 1;
        for(i; i < choices.length; i=i+1){
            choices[i]['val'] = lastChoiceValue;
            $("span.bullet", $("#options_list li").eq(i)).html(lastChoiceValue + ".");
            lastChoiceValue = DW.next_option_value(lastChoiceValue);//lastChoiceValue + 1;
        }
        questionnaireViewModel.selectedQuestion().choices.remove(choice);
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
    },
    selectedQuestion: ko.observable({}),
    changeSelectedQuestion: function(question) {
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        questionnaireViewModel.set_old_values(question);
        $(this).addClass("question_selected");
        DW.close_the_tip_on_period_question();
    },
    set_old_values: function(question){
        if(question){
            if(question.event_time_field_flag()){
                DW.report_period_date_format_change_warning.old_date_format = question.date_format();
            }
            DW.option_warning_dialog.old_question_type = question.type();
        }
    },
    clearChoices: function() {
        questionnaireViewModel.selectedQuestion().choices([]);
    },
    changeTextOfOption: function(choice) {
        if(!is_edit){
            return;
        }

        var curText = choice.value;
        var choices = questionnaireViewModel.selectedQuestion().options.choices;
        var changePrompt = false;
        var oldText = null;
        var opt_index = 0;
        $(choices).each(function(index, choiceInModel){
           if (choiceInModel.val == choice.option_val && choiceInModel.text.en != curText){
               changePrompt = true;
               oldText =  choiceInModel.text.en;
               opt_index = index;
           }
        });
        if(changePrompt){
            DW.change_option_text(choice,oldText, opt_index);
        }
    },
    remove_option: function(choice){
        function is_in(choice, choices){
            for(var index in choices){
                if(choices[index].val == choice.val){
                    return true;
                }
            }
            return false;
        };

        if(!is_edit){
            questionnaireViewModel.removeOptionFromQuestion(choice);
            return;
        }

        var choices = questionnaireViewModel.selectedQuestion().options.choices;
        if(!is_in(choice, choices)){
            questionnaireViewModel.removeOptionFromQuestion(choice);
            return;
        }

        if (choice.val == choices[choices.length - 1].val) {
            DW.option_warning_dialog.show_warning(gettext("You have deleted an answer choice.<br>If you have previously collected data for this choice it will be deleted.<br><br>Are you sure you want to continue?"));
        } else {
            DW.option_warning_dialog.show_warning(gettext('You have deleted an answer choice.<br>If you have previously collected data for this choice it will be deleted.<br><br>Also, the position of your answer choices has changed (Example: You have deleted “A. Cat”, so “B. Dog” is now “A. Dog”).<br>If you have previously collected data it will be adjusted to the new choice in that position (Example: The choice “Cat”, it will be replaced with “Dog”).<br><br>Are you sure you want to continue?'));
        }
        DW.option_warning_dialog.continueEventHandler = function(){
            questionnaireViewModel.removeOptionFromQuestion(choice);};
    },
    changeQuestionType: function(type_selector){
        var type_equal = type_selector.value == DW.option_warning_dialog.old_question_type
            || (type_selector.value == 'choice' && (DW.option_warning_dialog.old_question_type.indexOf('select')>=0));
        if(!is_edit || type_equal){
            return;
        }
        var type = questionnaireViewModel.selectedQuestion().type();
        var choices = questionnaireViewModel.selectedQuestion().choices();
        DW.option_warning_dialog.show_warning(gettext("You have changed the Answer Type.<br>If you have previously collected data, it may be rendered incorrect.<br><br>Are you sure you want to continue?"));
        DW.option_warning_dialog.cancelEventHandler = function(){
            questionnaireViewModel.selectedQuestion().type(type);
            questionnaireViewModel.selectedQuestion().choices(choices);
        };
    },
    showLengthLimiter: function() {
        return questionnaireViewModel.selectedQuestion().length_limiter() == 'length_limited';
    },
    set_all_questions_as_old_questions:function(){
        for (var question_index in questionnaireViewModel.questions()){
            questionnaireViewModel.questions()[question_index].newly_added_question(false)
        }
    },
    choiceCanBeDeleted: function() {
        return questionnaireViewModel.selectedQuestion().choices().length > 1 && questionnaireViewModel.isEnabled();
    },
    isEnabled: function(){
        if($("#not_wizard").length>0){
            return questionnaireViewModel.selectedQuestion().isEnabled();
        }
        else{
            return true;
        }
    },
    isTypeEnabled: function(){
        return questionnaireViewModel.isEnabled() && !questionnaireViewModel.selectedQuestion().event_time_field_flag();
    }
};