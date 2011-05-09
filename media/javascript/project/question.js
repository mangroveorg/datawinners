(function(){
    DW.questionnaire = function(question_list){
        this.question_list = question_list;
        this._init();
        console.log(question_list)
    }
    DW.questionnaire.prototype = {
        _init: function(){
            var self = this;
            self.question_list.forEach(function(question){
                var min_range =0;
                var max_range =null;
                if (question.range && question.type=="integer"){
                    min_range = question.range.min;
                    max_range = question.range.max;
                }
                var min_length=1;
                var max_length=null;
                if (question.length && question.type=="text"){
                    min_length = question.length.min;
                    max_length = question.length.max;
                }
                var newQuestion = new self._createQuestion(question.name,question.question_code,question.type,[],question.entity_question_flag, min_range, max_range,min_length,max_length);
                var loaded_question = viewModel.loadQuestion(newQuestion);
            });
        },
        _createQuestion : function(title,code,type,choices,entity_question,range_min,range_max,min_length,max_length){
            this.title=ko.observable(title);
            this.code=ko.observable(code);
            this.type=ko.observable(type);
            this.choices= ko.observableArray(choices);
            this.is_entity_question = ko.observable(entity_question);
            this.range_min = ko.observable(range_min);
            this.range_max = ko.observable(range_max);
            this.min_length = ko.observable(min_length);
            this.max_length = ko.observable(max_length);
            this.canBeDeleted = function(){return !this.is_entity_question();};
            this.isAChoiceTypeQuestion = ko.dependentObservable({
                read:function(){
                    return this.type() == "select"||this.type() == "select1"? "choice" : "none";},
                write:function(value){
                    this.type(this.type() == "" ? "select":"select1");
                },
                owner: this
            });
        },
        _textQuestion : function(){

        },
        _integerQuestion : function(){

        }

    }
})();
$(document).ready(function(){
    new DW.questionnaire(question_list);
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