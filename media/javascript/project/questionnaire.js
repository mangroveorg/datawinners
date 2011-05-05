// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
//var viewModel = null;
 function Question(title,code,type,choices,entity_question,range_min,range_max){
                            this.title=ko.observable(title);
                            this.code=ko.observable(code);
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
            var question = new Question("Question","code","text",[],false,0,"");
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
        var min =0;
        var max =null;
        if (question.range){
            min = question.range.min;
            max = question.range.max;
        }
        viewModel.loadQuestion(new Question(question.name,question.question_code,question.type,[],question.entity_question_flag, min, max));
     });
    viewModel.selectedQuestion(viewModel.questions()[0]);
    viewModel.selectedQuestion.valueHasMutated();

    ko.applyBindings(viewModel);

    $.validator.addMethod('spacerule', function(value, element, params) {
        var list = $('#' + element.id).val().split(" ");
        if (list.length > 1) {
            return false;
        }
        return true;
    }, "Space is not allowed in question code.");

    $.validator.addMethod('regexrule', function(value, element, params) {
        var text = $('#' + element.id).val();
        var re = new RegExp('^\\w+$');
        return re.test(text);
    }, "Only letters, digits and underscore is valid.");

//    //$('#code').rules("add", {spacerule:null});

    $("#question_form").validate({
        rules: {
            question:{
                required: true
            },
            code:{
                required: true,
                spacerule: true,
                regexrule: true
            },
            type:{
                required: true
            }
        }
    });

    $("#submit-button").click(function() {

        var data = JSON.stringify(ko.toJS(viewModel.questions()), null, 2);
        if ($.trim($("#questionnaire-code").val()) == "") {
            $("#questionnaire-code-error").html("<label class='error_message'> The Questionnaire code is required.</label>");
            return;
        }
        var list = $('#questionnaire-code').val().split(" ");
        if (list.length > 1) {
            $("#questionnaire-code-error").html("<label class='error_message'> Space is not allowed in questionnaire code.</label>");
            return;
        }
        var text = $('#questionnaire-code').val();
        var re = new RegExp('^\\w+$');
        if( !re.test(text)){
            $("#questionnaire-code-error").html("<label class='error_message'> Only letters, digits and underscore is valid.</label>");
            return;
        }
        $("#questionnaire-code-error").html("");

        if(!$('#question_form').valid()){
            $("#message-label").html("<label class='error_message'> This form has an error </label> ");
            hide_message();
            return;
        }
        var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':data,'pid':$('#project-id').val()}

        $.post('/project/questionnaire/save', post_data, function(response) {
            $("#message-label").html("<label class='success_message'>" + response + "</label>");
            hide_message();
        }).error(function(e){
            $("#message-label").html("<label class='error_message'>" + e.responseText + "</label>");
        });
    });

    function hide_message(){
        $('#message-label label').delay(5000).fadeOut();
    }
});