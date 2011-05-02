// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
//var viewModel = null;
 function Question(title,code,description,type,choices,entity_question,range_min,range_max){
                            this.title=ko.observable(title);
                            this.code=ko.observable(code);
                            this.description=ko.observable(description);
                            this.type=ko.observable(type);
                            this.choices= ko.observableArray(choices);
                            this.is_entity_question = ko.observable(entity_question);
                            this.range_min = ko.observable(range_min);
                            this.range_max = ko.observable(range_max);
                            this.canBeDeleted = function(){return !this.is_entity_question();};
                            this.isAChoiceTypeQuestion = ko.dependentObservable({
                                read:function(){
                                    return this.type() == "select"||this.type() == "select1"? "choice" : "none";},
                                write:function(value){
                                    this.type(this.type() == "" ? "select":"select1");
                                },
                                owner: this
                            });
 };

var viewModel =
    {
        questions : ko.observableArray([]),
        addQuestion : function(){
            var question = new Question("Question","code","","text",[],false,0,0);
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
    question_list.forEach(function(question){
        viewModel.loadQuestion(new Question(question.name,question.question_code,question.label.eng,question.type,[],question.entity_question_flag, question.range_min, question.range_max));
     });

    viewModel.addQuestion();

    ko.applyBindings(viewModel);

    $("#submit-button").click(function(){
        var data = JSON.stringify(ko.toJS(viewModel.questions()), null,2);
        $.post('/project/questionnaire/save', data,function(response){$("#message-label").html("<label>"+response+"</label>")});
    });
})