var viewModel =
    {
        questions : ko.observableArray([]),
        addQuestion : function(){
        var question = new DW.question();
            question.display = ko.dependentObservable(function(){
                return this.title() + ' ' + this.code();
            }, question);
            viewModel.questions.push(question);
            viewModel.selectedQuestion(question);
            viewModel.selectedQuestion.valueHasMutated();
            viewModel.questions.valueHasMutated();
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
            return viewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice"
        },
        showAddRange:function(){
            return viewModel.selectedQuestion().type() == 'integer';
        },
        showAddTextLength:function(){
            return viewModel.selectedQuestion().type() == 'text';
        },
        addOptionToQuestion: function(){
            viewModel.selectedQuestion().choices.push({value:''});
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
        }

    };