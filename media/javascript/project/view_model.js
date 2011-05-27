var viewModel =
    {
        questions : ko.observableArray([]),
        addQuestion : function(){
        var question = new DW.question();
            question.display = ko.dependentObservable(function(){
                return this.title() + ' ' + this.code();
            }, question);
            var test_code = DW.generateQuestionCode();
//            question.options.code =
            question.code(viewModel.check_unique_code(test_code))
            viewModel.questions.push(question);
            viewModel.selectedQuestion(question);
            viewModel.selectedQuestion.valueHasMutated();
            viewModel.questions.valueHasMutated();
            DW.charCount();
        },
        loadQuestion: function(question){
            question.display = ko.dependentObservable(function(){
                return this.title() + ' ' + this.code();
            }, question);
            viewModel.questions.push(question);
            viewModel.questions.valueHasMutated();
        },
        canQuestionBeDeleted: function(){
            return viewModel.questions().length>2
        },
        removeQuestion: function(question){
            viewModel.questions.remove(question);
            viewModel.changeSelectedQuestion(viewModel.questions()[0]);

        },
        showAddChoice:function(){
            if(viewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice"){
                if(viewModel.selectedQuestion().choices().length == 0){
                    viewModel.addOptionToQuestion();
                    viewModel.selectedQuestion().choices.valueHasMutated();
                }
                return true;
            }
            return false;
        },
        showDateFormats:function(){
            return viewModel.selectedQuestion().type() == "date"
        },
        showAddRange:function(){
            return viewModel.selectedQuestion().type() == 'integer';
        },
        showAddTextLength:function(){
            return viewModel.selectedQuestion().type() == 'text';
        },
        addOptionToQuestion: function(){
            viewModel.selectedQuestion().choices.push({text:"", val:""});
            viewModel.selectedQuestion().choices.valueHasMutated();
            viewModel.selectedQuestion.valueHasMutated();
            viewModel.questions.valueHasMutated();
        },
        removeOptionFromQuestion:function(choice){
            viewModel.selectedQuestion().choices.remove(choice);
            viewModel.selectedQuestion.valueHasMutated();
        },
        selectedQuestion: ko.observable({}),
        changeSelectedQuestion: function(question){
            viewModel.selectedQuestion(question);
            viewModel.selectedQuestion.valueHasMutated();
            viewModel.questions.valueHasMutated();
        },
        clearChoices: function(){
            viewModel.selectedQuestion().choices([]);
        },
        showLengthLimiter: function(){
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
        }

    };