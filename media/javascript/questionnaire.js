// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
var viewModel = null;
$(document).ready(function(){
    viewModel =
    {
        questions : ko.observableArray([]),
        addQuestion : function(){
            question = {title:ko.observable(''), code:ko.observable(''), description: ko.observable(''), type:ko.observable('text'), choices: ko.observableArray([])};
            viewModel.questions.push(question);
            viewModel.selectedQuestion(question);
            viewModel.selectedQuestion.valueHasMutated();
            viewModel.questions.valueHasMutated();
        },
        removeQuestion: function(question){
            viewModel.questions.remove(question);
            viewModel.changeSelectedQuestion(viewModel.questions()[0]);
        },
        addOptionToQuestion: function(question){
            question.choices.push('');
            question.choices.valueHasMutated();
        },
        selectedQuestion: ko.observable({}),
        changeSelectedQuestion: function(question){
            viewModel.selectedQuestion(question);
            viewModel.selectedQuestion.valueHasMutated();
            viewModel.questions.valueHasMutated();
        }
    };
    viewModel.addQuestion();

    viewModel.displayQuestion =ko.dependentObservable(function(){
            return this.selectedQuestion().title();
    },viewModel);

    ko.applyBindings(viewModel);
})