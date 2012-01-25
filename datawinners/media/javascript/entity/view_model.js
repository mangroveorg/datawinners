var viewModel =
{
    questions : ko.observableArray([]),
    hasAddedNewQuestions : false,

    addQuestion : function() {
        var question = new DW.question();
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        question.loaded(false);
        var test_code = DW.generateQuestionCode();
        question.code(viewModel.check_unique_code(test_code));
        var id_question = viewModel.questions.pop();
        viewModel.questions.push(question);
        viewModel.selectedQuestion(question);
        viewModel.selectedQuestion.valueHasMutated();
        viewModel.questions.push(id_question);
        viewModel.questions.valueHasMutated();
        DW.charCount();
        viewModel.hasAddedNewQuestions = true;
    },
    loadQuestion: function(question) {
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        viewModel.questions.push(question);
        viewModel.questions.valueHasMutated();
    },
    canQuestionBeDeleted: function() {
        return viewModel.questions().length > 2;
    },
    removeQuestion: function(question) {
        var index = $.inArray(question, viewModel.questions());
        viewModel.questions.remove(question);
        if(viewModel.questions().length == 0){
            DW.current_code = 1;
            viewModel.addQuestion();
            return;
        }
        var next_index = (index) % viewModel.questions().length;
        if(index == viewModel.questions().length){
            DW.current_code -= 1;
        }
        viewModel.changeSelectedQuestion(viewModel.questions()[next_index]);
        viewModel.hasAddedNewQuestions = true;
        viewModel.reassignQuestionCodes(index);
    },
    removeQuestionCheck:function(question){
        $("#delete_warning").dialog("open");
        $("#delete_ok").unbind('click').click(function(){
            viewModel.removeQuestion(question);
            $("#delete_warning").dialog("close");
        });
        $("#delete_cancel").unbind('click').click(function(){
            $("#delete_warning").dialog("close");
            return false;
        });
    },
    removeIfQuestionIsSelectedQuestion: function(question) {
        if (viewModel.selectedQuestion() == question) {
            viewModel.removeQuestion(question);
        }
    },
    showAddChoice:function() {
        if (viewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice") {
            if (viewModel.selectedQuestion().choices().length == 0) {
                viewModel.addOptionToQuestion();
                viewModel.selectedQuestion().choices.valueHasMutated();
            }
            return true;
        }
        return false;
    },
    showDateFormats:function() {
        return viewModel.selectedQuestion().type() == "date";
    },
    showAddRange:function() {
        return viewModel.selectedQuestion().type() == 'integer';
    },
    showAddTextLength:function() {
        return viewModel.selectedQuestion().type() == 'text';
    },
    addOptionToQuestion: function() {
        var lastChoice = viewModel.selectedQuestion().choices()[viewModel.selectedQuestion().choices().length - 1];
        viewModel.selectedQuestion().choices.push({text:"", val:String.fromCharCode(lastChoice.val.charCodeAt(0) + 1)});
        viewModel.selectedQuestion().choices.valueHasMutated();
        viewModel.selectedQuestion.valueHasMutated();
        viewModel.questions.valueHasMutated();
    },
    removeOptionFromQuestion:function(choice) {
        var choices = viewModel.selectedQuestion().choices();
        var indexOfChoice = $.inArray(choice, choices);
        var lastChoiceValue = choice['val'].charCodeAt(0);
        var i = indexOfChoice + 1;
        for(i; i < choices.length; i=i+1){
            choices[i]['val'] = String.fromCharCode(lastChoiceValue);
            lastChoiceValue = lastChoiceValue + 1;
        }
        viewModel.selectedQuestion().choices.remove(choice);
        viewModel.selectedQuestion.valueHasMutated();
    },
    selectedQuestion: ko.observable({}),
    changeSelectedQuestion: function(question) {
        viewModel.selectedQuestion(question);
        viewModel.selectedQuestion.valueHasMutated();
        viewModel.questions.valueHasMutated();
        $(this).addClass("question_selected");
    },
    clearChoices: function() {
        viewModel.selectedQuestion().choices([]);
    },
    showLengthLimiter: function() {
        return viewModel.selectedQuestion().length_limiter() == 'length_limited';
    },
    check_unique_code: function(test_code) {
        var q;
        for (q in viewModel.questions()) {
            if (test_code == viewModel.questions()[q].code()) {
                test_code = DW.generateQuestionCode();
                test_code = viewModel.check_unique_code(test_code);
                return test_code;
            }
        }
        return test_code;
    },
    choiceCanBeDeleted: function() {
        return viewModel.selectedQuestion().choices().length > 1 && viewModel.isEnabled();
    },
    isEnabled: function(){
        if($("#not_wizard").length>0){
            return viewModel.selectedQuestion().isenabled();
        }
        else{
            return true;
        }
    },
    isTypeEnabled: function(){
        return viewModel.isEnabled() && !viewModel.selectedQuestion().event_time_field_flag() && !viewModel.selectedQuestion().loaded();
    },
    reassignQuestionCodes:function(index){
        DW.current_code = index+1;
        var new_code = DW.current_code;
        for ( var i=index;i< viewModel.questions().length;i++){
            viewModel.questions()[i].code(DW.generateQuestionCode());
        }
    }
};