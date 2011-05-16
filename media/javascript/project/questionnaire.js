// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

//DW is the global name space for DataWinner
DW.question = function(question){
    var defaults = {
        name : "Question",
        question_code : "code",
        type : "text",
        choices :[{text:"", val:""}],
        entity_question_flag : false,
        length : {
          min : 1,
          max : 12
        },
        range : {
          min : 0,
          max : ""
        },
        date_format: "mm.yyyy"
    };

    // Extend will override the default values with the passed values(question), And take the values from defaults when its not present in question
    this.options = $.extend({},defaults, question);
    this._init();
}
DW.question.prototype = {
    _init : function(){
        var q = this.options;
        this.range_min = ko.observable(q.range.min);
        
        //This condition required especially because in DB range_max is a mandatory field
        this.range_max = ko.observable(q.range.max ? q.range.max : "");

        this.min_length = ko.observable(q.length.min);
        this.max_length = ko.observable(q.length.max);
        this.title = ko.observable(q.name);
        this.code = ko.observable(q.question_code);
        this.type = ko.observable(q.type);
        this.choices = ko.observableArray(q.choices);
        this.is_entity_question = ko.observable(q.entity_question_flag);
        this.canBeDeleted = function(){return !this.is_entity_question();}
        this.isAChoiceTypeQuestion = ko.dependentObservable({
            read:function(){
                return this.type() == "select"||this.type() == "select1"? "choice" : "none";},
            write:function(value){
                this.type(this.type() == "" ? "select":"select1");
            },
            owner: this
        });
        this.date_format = ko.observable(q.date_format);
    }
};

$(document).ready(function(){
    question_list.forEach(function(question){
        var questions = new DW.question(question);
        viewModel.loadQuestion(questions);
     })
    viewModel.selectedQuestion(viewModel.questions()[0]);
    viewModel.selectedQuestion.valueHasMutated();

    ko.applyBindings(viewModel);

    $.validator.addMethod('spacerule', function(value, element, params) {
        var list = $.trim($('#' + element.id).val()).split(" ");
        if (list.length > 1) {
            return false;
        }
        return true;
    }, "Space is not allowed in question code.");

    $.validator.addMethod('regexrule', function(value, element, params) {
        var text = $('#' + element.id).val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        return re.test(text);
    }, "Only letters and digits are valid.");

     $.validator.addMethod('naturalnumberrule', function(value, element, params) {
        var num = $('#' + element.id).val();
        return num != 0;
    }, "Answer cannot be of length less than 1");

//    //$('#code').rules("add", {spacerule:null});

    $("#question_form").validate({
     messages: {
         min_length:{
             digits: "Please enter positive numbers only"
         },
         max_length:{
             digits: "Please enter positive numbers only"
         }

     },
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
            },
            min_length:{
                digits: true,
                naturalnumberrule:true
            },
            max_length:{
                digits:true,
                naturalnumberrule:true
            },
            range_min:{
                number: true
            },
            range_max:{
                number: true
            }

        }
    });

    $("#submit-button").click(function() {

        var data = JSON.stringify(ko.toJS(viewModel.questions()), null, 2);
        if ($.trim($("#questionnaire-code").val()) == "") {
            $("#questionnaire-code-error").html("<label class='error_message'> The Questionnaire code is required.</label>");
            return;
        }

        var list = $.trim($('#questionnaire-code').val()).split(" ");
        if (list.length > 1) {
            $("#questionnaire-code-error").html("<label class='error_message'> Space is not allowed in questionnaire code.</label>");
            return;
        }
        else{
            $('#questionnaire-code').val($.trim($('#questionnaire-code').val()))
        }

        var text = $('#questionnaire-code').val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        if( !re.test(text)){
            $("#questionnaire-code-error").html("<label class='error_message'> Only letters and digits are valid.</label>");
            return;
        }

        $("#questionnaire-code-error").html("");

        if(!$('#question_form').valid()){
            $("#message-label").html("<label class='error_message'> This questionnaire has an error.</label> ");
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

    $('input[name=type]:radio').change(
            function(){
                viewModel.selectedQuestion().range_min(0);
                viewModel.selectedQuestion().range_max("");
                viewModel.selectedQuestion().min_length(1);
                viewModel.selectedQuestion().max_length(12);
                viewModel.selectedQuestion().choices([{text:"", val:'a'}]);
            }
    )
});