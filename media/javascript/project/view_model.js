var viewModel =
{
    questions : ko.observableArray([]),

    addQuestion : function() {
        var question = new DW.question();
        question.display = ko.dependentObservable(function() {
            return this.title() + ' ' + this.code();
        }, question);
        question.loaded(false);
        var test_code = DW.generateQuestionCode();
//            question.options.code =
        question.code(viewModel.check_unique_code(test_code))
        viewModel.questions.push(question);
        viewModel.selectedQuestion(question);
        viewModel.selectedQuestion.valueHasMutated();
        viewModel.questions.valueHasMutated();
        DW.charCount();
        DW.smsPreview();
    },
    loadQuestion: function(question) {
        question.display = ko.dependentObservable(function() {
            return this.title() + ' ' + this.code();
        }, question);
        viewModel.questions.push(question);
        viewModel.questions.valueHasMutated();
    },
    canQuestionBeDeleted: function() {
        return viewModel.questions().length > 2
    },
    removeQuestion: function(question) {
        var index = $.inArray(question, viewModel.questions());
        viewModel.questions.remove(question);
        var next_index = (index) % viewModel.questions().length;
        viewModel.changeSelectedQuestion(viewModel.questions()[next_index]);

    },
    removeIfQuestionIsSelectedQuestion: function(question) {
        if (viewModel.selectedQuestion() == question) {
            viewModel.removeQuestion(question)
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
        return viewModel.selectedQuestion().type() == "date"
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
        var indexOfChoice = viewModel.selectedQuestion().choices().indexOf(choice);
        var lastChoiceValue = choice['val'].charCodeAt(0);
        for(var i = indexOfChoice + 1; i < viewModel.selectedQuestion().choices().length; i++){
            viewModel.selectedQuestion().choices()[i]['val'] = String.fromCharCode(lastChoiceValue);
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
        return viewModel.selectedQuestion().length_limiter() == 'length_limited'
    },
    check_unique_code: function(test_code) {
        for (var q in viewModel.questions()) {
            if (test_code == viewModel.questions()[q].code()) {
                test_code = DW.generateQuestionCode();
                test_code = viewModel.check_unique_code(test_code);
                return test_code;
            }
        }
        return test_code;
    },
    choiceCanBeDeleted: function() {
        return viewModel.selectedQuestion().choices().length > 1 && viewModel.isEnabled()
    },
    isEnabled: function(){
        if($("#not_wizard").length>0){
            return viewModel.selectedQuestion().isenabled();
        }
        else
            return true;
    }
};