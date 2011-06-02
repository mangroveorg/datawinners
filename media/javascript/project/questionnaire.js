// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

//DW is the global name space for DataWinner
DW.question = function(question) {
    var defaults = {
        name : "Question",
        code : "code",
        type : "text",
        choices :[
            {text:"", val:""}
        ],
        entity_question_flag : false,
        length_limiter : "length_unlimited",
        length : {
            min : 1,
            max : ""
        },
        range : {
            min : 0,
            max : ""
        },
        date_format: "mm.yyyy"
    };

    // Extend will override the default values with the passed values(question), And take the values from defaults when its not present in question
    this.options = $.extend({}, defaults, question);
    this._init();
};


DW.question.prototype = {
    _init : function() {
        var q = this.options;
        this.range_min = ko.observable(q.range.min);

        //This condition required especially because in DB range_max is a mandatory field
        this.range_max = ko.observable(q.range.max ? q.range.max : "");

        this.min_length = ko.observable(q.length.min);
        this.max_length = ko.observable(q.length.max);
        this.title = ko.observable(q.name);
        this.code = ko.observable(q.code);
        this.type = ko.observable(q.type);
        this.choices = ko.observableArray(q.choices);
        this.is_entity_question = ko.observable(q.entity_question_flag);
        this.canBeDeleted = function() {
            return !this.is_entity_question();
        };
        this.isAChoiceTypeQuestion = ko.dependentObservable({
                    read:function() {
                        return this.type() == "select" || this.type() == "select1" ? "choice" : "none";
                    },
                    write:function(value) {
                        this.type(this.type() == "" ? "select" : "select1");
                    },
                    owner: this
                });
        this.date_format = ko.observable(q.date_format);
        this.length_limiter = ko.observable(q.length.max ? "length_limited" : "length_unlimited");
    }
};

DW.current_code = "AA";

DW.generateQuestionCode = function() {
    var code = DW.current_code;
    var next_code = DW.current_code;
    var x,y = '';
    if (next_code[1] < 'Z') {
        y = String.fromCharCode(next_code[1].charCodeAt() + 1);
        x = next_code[0];
    }
    else {
        x = String.fromCharCode(next_code[0].charCodeAt() + 1);
        y = 'A';
    }
    next_code = x + y;
    DW.current_code = next_code;
    return code
};

DW.charCount = function() {
    var questionnaire_code_len = $('#questionnaire-code').val().length;
    var question_codes_len = 0;
    var selected_question_code_difference = 0;
    var max_len = 160;
    var constraints_len = 0;
    var space_len = 1;
    var delimiter_len = 1;
    var sms_number = 1;
    var sms_number_text = "";

    for (var i = 0; i < viewModel.questions().length; i++) {
        var current_question = viewModel.questions()[i];
        question_codes_len = question_codes_len + current_question.code().length + space_len + delimiter_len;
        var question_type = current_question.type();
        switch (question_type) {
            case 'integer':
                constraints_len = constraints_len + current_question.range_max().toString().length;
                break;
            case 'text':
                if (current_question.max_length()) {
                    constraints_len = constraints_len + parseInt(current_question.max_length());
                }
                break;
            case 'date':
                constraints_len = constraints_len + current_question.date_format().length;
                break;
            case 'select':
                constraints_len = constraints_len + current_question.choices().length;
                break;
            case 'select1':
                constraints_len = constraints_len + 1;
                break;
        }
        constraints_len = constraints_len + delimiter_len;
    }
    var current_len = questionnaire_code_len + question_codes_len + constraints_len + selected_question_code_difference;
    if (current_len <= max_len) {
        $("#char-count").css("color", "#666666")
    }
    if (current_len > max_len) {
        $("#char-count").css("color", "red")
        max_len = max_len+160;
        sms_number++;
        sms_number_text = " (" + sms_number + ")";
    }
    $('#char-count').html((current_len) + ' / ' + max_len + sms_number_text + ' characters used');

};

$(document).ready(function() {
    question_list.forEach(function(question) {
        var questions = new DW.question(question);
        viewModel.loadQuestion(questions);
    });
    viewModel.selectedQuestion(viewModel.questions()[0]);
    viewModel.selectedQuestion.valueHasMutated();

    ko.applyBindings(viewModel);
    DW.charCount();
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
    $('.delete').live("click", DW.charCount);

    //The Questionnarie left navigation toggle functions
    $("#questions-panel .add_question .add_link").click(function(){
        $('.question_list ol > div:last').toggleClass("question_selected");
        $('.question_list ol > div:last').find(".selected_question_arrow").show();
    });
    $('.question_list ol > div:first').toggleClass("question_selected");
    $('.question_list ol > div:first').find(".selected_question_arrow").show();

    $('.question_list ol div .delete_link').live("click", function(event){
        event.stopPropagation();
        $('.question_list ol > div:first').toggleClass("question_selected");

    })
    $('.question_list ol > div').live("click", function(){
        var selected = $(this).index()+1;
        var selected_div = $('.question_list ol').find("div:nth-child("+selected+")");
            selected_div.toggleClass("question_selected");
            selected_div.find(".selected_question_arrow").show();
    });


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

    $("#question_form").validate({
                messages: {
                    max_length:{
                        digits: "Please enter positive numbers only"
                    }

                },
                rules: {
                    question_title:{
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
                    max_length:{
                        digits:true
                    },
                    range_min:{
                        number: true
                    },
                    range_max:{
                        number: true
                    },
                    choice_text:{
                        required: "#choice_text:visible"
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
        else {
            $('#questionnaire-code').val($.trim($('#questionnaire-code').val()))
        }

        var text = $('#questionnaire-code').val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        if (!re.test(text)) {
            $("#questionnaire-code-error").html("<label class='error_message'> Only letters and digits are valid.</label>");
            return;
        }

        $("#questionnaire-code-error").html("");

        if (!$('#question_form').valid()) {
            $("#message-label").html("<label class='error_message'> This questionnaire has an error.</label> ");
            hide_message();
            return;
        }

        var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':data,'pid':$('#project-id').val()}

        $.post('/project/questionnaire/save', post_data,
                function(response) {
                    $("#message-label").html("<label class='success_message'>" + response + "</label>");
                    hide_message();
                }).error(function(e) {
            $("#message-label").html("<label class='error_message'>" + e.responseText + "</label>");
        });
    });

    function hide_message() {
        $('#message-label label').delay(5000).fadeOut();
    }

    $('input[name=type]:radio').change(
            function() {
                viewModel.selectedQuestion().range_min(0);
                viewModel.selectedQuestion().range_max("");
                viewModel.selectedQuestion().min_length(1);
                viewModel.selectedQuestion().max_length("");
                viewModel.selectedQuestion().length_limiter("length_unlimited");
                viewModel.selectedQuestion().choices([
                    {text:"", val:'a'}
                ]);
            }
    );
    $('input[name=text_length]:radio').change(
            function() {
                viewModel.selectedQuestion().max_length("");
            }
    )
});