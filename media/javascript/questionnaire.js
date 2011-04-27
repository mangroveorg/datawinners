// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
//var viewModel = null;
function Question(title,code,description,type,choices){
                        this.title=ko.observable(title);
                        this.code=ko.observable(code);
                        this.description=ko.observable(description);
                        this.type=ko.observable(type);
                        this.choices= ko.observableArray(choices);
                        }
 var viewModel =
    {
        questions : ko.observableArray([]),
        addQuestion : function(){
            var question = new Question("Question","code","","text",[]);
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
            return viewModel.questions().length>1
        },
        removeQuestion: function(question){
            viewModel.questions.remove(question);
            viewModel.changeSelectedQuestion(viewModel.questions()[0]);
        },
        showAddChoice:function(){
            return viewModel.selectedQuestion().type() == 'choice';
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

$(document).ready(function(){
    viewModel.addQuestion();
    ko.applyBindings(viewModel);

    $("#submit-button").click(function(){
        var data = JSON.stringify(ko.toJS(viewModel.questions()), null,2);
        $.post('/project/questionnaire/save', data,function(response){$("#message-label").append("<label>"+response+"</label>")});
    });
})