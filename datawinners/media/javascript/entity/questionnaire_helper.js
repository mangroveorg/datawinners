DW.ko = {
        createValidatableObservable: function(options){
                var defaults = {value: "", valid: true, error: ""};
                var params = $.extend({}, defaults, options);

                var observable = ko.observable(params.value);
                observable.valid = ko.observable(params.valid);
                observable.error = ko.observable(params.error);
                observable.clearError = function(){
                  this.valid(true);
                  this.error("");
                };
                observable.setError = function(message){
                  this.valid(false);
                  this.error(message);
                };
                return observable;
            },
        createValidatableObservableObject: function(options){
                var defaults = {value: [], valid: ko.observable(true), error: ko.observable("")};
                var observable = $.extend({}, defaults, options);
                observable.clearError = function(){
                  this.valid(true);
                  this.error("");
                };
                observable.setError = function(message){
                  this.valid(false);
                  this.error(message);
                };
                return observable;
            }
};



//DW is the global name space for DataWinner
DW.init_inform_datasender_about_changes = function () {
    kwargs = {container: "#inform_datasender_about_changes",
        is_continue: true,
        title: gettext('Inform Your Data Senders about the Changes'),
        continue_handler: function () {
            if (typeof(this.redirect_url) != "undefined") {
                window.location.replace(this.redirect_url);
            }
        },
        cancel_handler: this.continue_handler
    };
    DW.inform_datasender_about_changes = new DW.warning_dialog(kwargs);
};

DW.init_empty_questionnaire_warning = function () {
    kwargs = {container: "#no_questions_exists", title: gettext('Warning: Empty questionnaire') }
    DW.empty_questionnaire_warning = new DW.warning_dialog(kwargs)
}

DW.check_empty_questionnaire = function () {
    if (questionnaireViewModel.questions().length == 0) {
        DW.empty_questionnaire_warning.show_warning();
        return false;
    }
    return true;
}

DW.instruction_template = {
    "number": gettext("Answer must be a number."),
    "min_number": gettext("Answer must be a number. The minimum is %d."),
    "max_number": gettext("Answer must be a number. The maximum is %d."),
    "range_number": gettext("Answer must be a number between %d-%d."),
    "text": gettext("Answer must be a word"),
    "max_text": gettext("Answer must be a word %d characters maximum"),
    "date": gettext("Answer must be a date in the following format: %s. Example: %s"),
    "single_select": gettext("Choose 1 answer from the list. Example: a"),
    "multi_select": gettext("Choose 1 or more answers from the list. Example: a or ab "),
    "gps": gettext("Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy Example: -18.1324,27.6547 "),
    "dd.mm.yyyy": "25.12.2011",
    "mm.dd.yyyy": "12.25.2011",
    "mm.yyyy": "12.2011",
    "unique_id_question": gettext("Answer must be 20 characters maximum"),
    "telephone_number": gettext("Answer must be country code plus telephone number. Example: 261333745269")
};
DW.date_template = {
    "dd.mm.yyyy": gettext("day.month.year"),
    "mm.dd.yyyy": gettext("month.day.year"),
    "mm.yyyy": gettext("month.year")

};
DW.question = function (question) {
//    var question_name = DW.next_question_name_generator();
    var defaults = {
        name: '',
        code: "code",
        required: true,
//        type:"text",
        language: 'en',
        choices: [],
        entity_question_flag: false,
        length_limiter: "length_unlimited",
        length: {
            min: 1,
            max: ""
        },
        range: {
            min: "",
            max: ""
        },
        label: "Question",
        date_format: "mm.yyyy",
        instruction: gettext("Answer must be a text"),
        newly_added_question: false,
        event_time_field_flag: false
    };

    // Extend will override the default values with the passed values(question), And take the values from defaults when its not present in question
    //first argument "true" in extend field shows that appent values in default
    this.options = $.extend(true, defaults, question);
    this._init();
};

DW.initChoices = function (choices) {
    var final_choices = [];
    $.each(choices, function (index, choice) {
        var display_choice = {};
        display_choice['text'] = choice.text;
        display_choice['val'] = choice.val;
//        display_choice['id'] = choice.id;
        final_choices.push(DW.ko.createValidatableObservable({value: display_choice}));
    });
    return final_choices;
};


DW.question.prototype = {
    _init: function () {
        var self = this;
        var q = this.options;
        this.newly_added_question = ko.observable(q.newly_added_question);
        this.range_min = DW.ko.createValidatableObservable({value: q.range.min});
        this.event_time_field_flag = ko.observable(q.event_time_field_flag);

        //This condition required especially because in DB range_max is a mandatory field
        this.range_max = DW.ko.createValidatableObservable({value: q.range.max});

        this.min_length = ko.observable(q.length.min);
        this.max_length = DW.ko.createValidatableObservable({value: q.length.max});

        if (DW.isRegistrationQuestionnaire()) {
            this.name = ko.observable(q.name);
            this.title = ko.observable(q.label);
        } else {
            this.title = DW.ko.createValidatableObservable({value: q.name});
        }

        this.code = ko.observable(q.code);
        this.type = ko.observable(q.type);
        this.is_entity_question = ko.observable(q.entity_question_flag);

        this.showDateFormats = ko.computed(function(){
            return this.type() == "date";
        }, this);

        this.showAddRange = ko.computed(function() {
            return this.type() == 'integer';
        }, this);

        this.showAddTextLength = ko.computed(function() {
            return this.type() == 'text' && !this.is_entity_question();
        }, this);

        this.required = ko.observable(q.required);

        this.answerType = DW.ko.createValidatableObservable();

        this.display = ko.computed(function() {
            return this.title();
        }, this);

        this.answerType.subscribe(function(selected_answer_type){
            if(selected_answer_type === "") return;
            clearErrors();
            DW.change_question_type_for_selected_question(selected_answer_type);
        }, this);

        var clearErrors = function(){
            self.max_length.clearError();
            self.range_max.clearError();
            self.range_min.clearError();
            clearChoiceErrors();
        };

        var initialValues = DW.initChoices(q.choices);
        this.choices = ko.observableArray(initialValues);

        this.choiceCanBeDeleted = ko.computed(function() {
            return this.choices().length > 1;
        }, this);

        this.removeOptionFromQuestion = function (choice) {
            self.checkForQuestionnaireChange(choice.value);
            var choices = self.choices();
            var indexOfChoice = $.inArray(choice, choices);
            var lastChoiceValue = choice.value.val();
            var i = indexOfChoice + 1;
            for (i; i < choices.length; i = i + 1) {
                choices[i].value.val(lastChoiceValue);
                $("span.bullet", $("#options_list li").eq(i)).html(lastChoiceValue + ".");
                lastChoiceValue = DW.next_option_value(lastChoiceValue);
            }
            self.choices.remove(choice);
        };

        var clearChoiceErrors = function(){
          ko.utils.arrayForEach(self.choices(), function(choice){
              choice.clearError();
          });
        };

        this.addOptionToQuestion = function() {
            var selectedQuestionCode = "a";
            if (this.choices().length > 0) {
                var lastChoice = this.choices()[this.choices().length - 1];
                selectedQuestionCode = DW.next_option_value(lastChoice.value.val());
            }
            this.choices.push(DW.ko.createValidatableObservableObject({value:{text: ko.observable(gettext("")), val: ko.observable(selectedQuestionCode)}}));
        };

        this.showAddChoice = function() {
            if (this.isAChoiceTypeQuestion() == "choice") {
                if (this.choices().length == 0) {
                    this.addOptionToQuestion();
                }
                return true;
            }
            return false;
        };


        this.checkForQuestionnaireChange = function(choice) {
            if (_.any($(this.options.choices), function (v) {
                return v.val == choice.val;
            })) {
                DW.questionnaire_was_changed = true;
            }
        };

        this.date_format = ko.observable(q.date_format);
        this.length_limiter = ko.observable(q.length.max ? "length_limited" : "length_unlimited");
//        same as ko.computed
        this.showLengthLimiter = ko.computed( function(){
            return this.length_limiter() == 'length_limited';
        }, this);

        this.length_limiter.subscribe(function(new_length_limiter){
            if(new_length_limiter == 'length_unlimited')
                this.max_length("");
                this.max_length.clearError();
        }, this);

        this.instruction = ko.dependentObservable({
            read: function () {
                if (this.is_entity_question() && this.max_length() == 20) {
                    return DW.instruction_template.unique_id_question;
                }

                if (this.type() == "text") {
                    if (this.max_length() != "" && this.max_length() > 0) {
                        return $.sprintf(DW.instruction_template.max_text, this.max_length());
                    }
                    return DW.instruction_template.text;
                }
                if (this.type() == "telephone_number") {
                    return $.sprintf(DW.instruction_template.telephone_number);
                }
                if (this.type() == "list") {
                    return DW.instruction_template.text;
                }
                if (this.type() == "integer") {
                    if (this.range_min() == "" && this.range_max() == "") {
                        return DW.instruction_template.number;
                    }
                    if (this.range_min() == "") {
                        return $.sprintf(DW.instruction_template.max_number, this.range_max());
                    }
                    if (this.range_max() == "") {
                        return $.sprintf(DW.instruction_template.min_number, this.range_min());
                    }
                    return $.sprintf(DW.instruction_template.range_number, this.range_min(), this.range_max());
                }
                if (this.type() == "date") {
                    return $.sprintf(DW.instruction_template.date, DW.date_template[this.date_format()], DW.instruction_template[this.date_format()]);
                }
                if (this.type() == "geocode") {
                    return DW.instruction_template.gps;
                }
                if (this.type() == "select1") {
                    return DW.instruction_template.single_select;
                }
                if (this.type() == "select") {
                    return DW.instruction_template.multi_select;
                }
                return "No instruction can be generated";
            },
            owner: this
        });
        this.canBeDeleted = function () {
            if (DW.isRegistrationQuestionnaire()) {
                return (!this.is_entity_question() && this.name() != 'name');
            } else {
                return (!this.is_entity_question());
            }
        };
        this.isAChoiceTypeQuestion = ko.dependentObservable({
            read: function () {
                return this.type() == "select" || this.type() == "select1" ? "choice" : "none";
            },
            write: function (value) {
                this.type(this.type() == "" ? "select" : "select1");
            },
            owner: this
        });

        var mandatoryValidator = function(observable){
            if(!observable()){
                observable.valid(false);
                observable.error(gettext("This field is required."));
            }
            else{
                observable.valid(true);
                observable.error("");
            }
        };

        var numericValidator = function(observable){
             if((observable()+"").match(/[0-9]+/)){
                observable.valid(true);
                observable.error("");
            }
            else{
                observable.valid(false);
                observable.error(gettext("Only numbers allowed."));
            }
        };

        this.validate = function(){
            mandatoryValidator(this.title);
            mandatoryValidator(this.answerType);
            if(this.showLengthLimiter()){
                mandatoryValidator(this.max_length);
                this.max_length.valid() && numericValidator(this.max_length);
            }
            else if(this.showAddRange()){
                this.range_min() && numericValidator(this.range_min);
                this.range_max() && numericValidator(this.range_max);
            }

            var isChoiceAnswerValid = true;
            if(this.showAddChoice()){
                ko.utils.arrayForEach(this.choices(), function(choice){
                    if(choice.value.text()){
                        choice.clearError();
                    }
                    else{
                        choice.valid(false);
                        choice.error(gettext("This field is required."));
                    }
                    isChoiceAnswerValid &= choice.valid();
                });
            }

            return this.title.valid() && this.answerType.valid() && this.max_length.valid()
                    && this.range_min.valid() && this.range_max.valid() && isChoiceAnswerValid;
        };

    }

};


DW.change_question_title_for_reporting_period = function (replaceto, replacewith) {
    $(questionnaireViewModel.questions()).each(function (question) {
        if (questionnaireViewModel.selectedQuestion().event_time_field_flag()) {
            var question_title = questionnaireViewModel.selectedQuestion().title();
            questionnaireViewModel.selectedQuestion().title(question_title.replace(replaceto, replacewith));
        }
    });
    questionnaireViewModel.questions.valueHasMutated();
};


DW.removeQuestionCheckForRegistration = function (question) {
    if (!DW.has_submission_delete_warning_for_entity.is_continue && DW.questionnaire_has_submission() && !question.newly_added_question()) {
        DW.has_submission_delete_warning_for_entity.show_warning();
    } else {
        questionnaireViewModel.removeQuestion(question);
    }
};

DW.removeQuestionCheckForSubmission = function (question) {
    var index = $.inArray(question, questionnaireViewModel.questions());
    if (questionnaireViewModel.questions()[index].event_time_field_flag()) {
        DW.delete_periodicity_question_warning.show_warning();
    } else if (is_edit && !DW.has_submission_delete_warning.is_continue && !question.newly_added_question() && DW.questionnaire_has_submission()) {
        DW.has_submission_delete_warning.show_warning();
    } else {
        questionnaireViewModel.removeQuestion(question);
    }
};

DW.isRegistrationQuestionnaire = function () {
    return $('#qtype').val() == 'subject';
};

DW.next_question_name_generator = function () {
    if (!DW.isRegistrationQuestionnaire()) {
        return 'Question ' + ($('div.question_list ol li').length + 1 );
    }
    var questionPattern = /^Question \d+$/;
    var max = 1;
    var questionName = "";
    var current = 1;
    for (var i = 0; i < questionnaireViewModel.questions().length; i++) {
        questionName = questionnaireViewModel.questions()[i].name();
        current = parseInt(questionName.substring(9));
        if (questionPattern.test(questionName) && max < current) {
            max = current;
        }
    }
    return 'Question ' + (Math.max(max, $('div.question_list ol li').length) + 1);
};

DW.next_option_value = function (lastChoice) {
    var nextOption = "a";
    if (lastChoice.charCodeAt(lastChoice.length - 1) == 122) {
        if (lastChoice.length == 2) {
            nextOption = String.fromCharCode(lastChoice.charCodeAt(0) + 1) + "a";
        } else {
            nextOption = "1a";
        }
    } else {
        nextOption = (lastChoice.length == 2) ? lastChoice[0] : "";
        nextOption += String.fromCharCode(lastChoice.charCodeAt(lastChoice.length - 1) + 1);
    }
    return nextOption;
}

DW.option_warning_dialog = {
    init: function () {
        DW.option_warning_dialog.continueEventHandler = function () {
        };
        DW.option_warning_dialog.cancelEventHandler = function () {
        };
        DW.option_warning_dialog.dialog_id = "#option_warning_message";
        DW.option_warning_dialog.init_warning_dialog();
        DW.option_warning_dialog.bind_cancel_link();
        DW.option_warning_dialog.bind_continue();
        DW.option_warning_dialog.bind_close();
    },
    init_warning_dialog: function () {
        $(DW.option_warning_dialog.dialog_id).dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: false,
            height: 'auto',
            width: 500,
            closeText: 'hide'
        });
    },
    bind_cancel_link: function () {
        $(DW.option_warning_dialog.dialog_id + "_cancel").bind("click", function () {
            $(DW.option_warning_dialog.dialog_id).dialog("close");
            DW.option_warning_dialog.cancelEventHandler();
            DW.hide_dialog_overlay();
        });
    },
    bind_close: function () {
        $('.ui-icon-closethick').bind("click", function () {
            $(DW.option_warning_dialog.dialog_id).dialog("close");
            DW.option_warning_dialog.cancelEventHandler();
            DW.hide_dialog_overlay();
        });
    },
    bind_continue: function () {
        $(DW.option_warning_dialog.dialog_id + "_continue").bind("click", function () {
            $(DW.option_warning_dialog.dialog_id).dialog("close");
            DW.option_warning_dialog.continueEventHandler();
            DW.hide_dialog_overlay();
        });
    },

    show_warning: function (message) {
        $("#option_warning_text")[0].innerHTML = message;
        $(DW.option_warning_dialog.dialog_id).dialog("open");
        DW.show_dialog_overlay();
    }
};

DW.close_the_tip_on_period_question = function () {
    if ($("#question_title").hasClass("blue_frame")) {
        $("#question_title").removeClass("blue_frame");
    }
    if ($("#periode_green_message").length > 0) {
        $("#periode_green_message").hide();
    }
}

DW.questionnaire_has_submission = function () {
    var subject_questionnaire = (typeof(is_edit) == "undefined");
    if (subject_questionnaire) {
        var entity_type = $("#entity-type").val();
        var url_get = $.sprintf("/alldata/entities/%s/", entity_type);
    } else {
        var form_code = $("#saved-questionnaire-code").val();
        var url_get = $.sprintf("/project/has_submission/%s/", form_code);
    }

    $.ajaxSetup({async: false});
    var return_value = true;
    $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
    $.ajax({
        type: 'GET',
        url: url_get,
        success: function (response) {
            $.ajaxSetup({async: true});
            $.unblockUI();

            if (subject_questionnaire) {
                return_value = response.length != 0;
            } else {
                var response_data = JSON.parse(response);
                return_value = response_data.has_data;
            }
        }
    });
    return return_value;
}

DW.init_question_constraints = function () {
    questionnaireViewModel.selectedQuestion().range_min("");
    questionnaireViewModel.selectedQuestion().range_max("");
    questionnaireViewModel.selectedQuestion().min_length(1);
    questionnaireViewModel.selectedQuestion().max_length("");
    questionnaireViewModel.selectedQuestion().length_limiter("length_unlimited");
    questionnaireViewModel.selectedQuestion().choices.push(DW.ko.createValidatableObservableObject({value: {text: ko.observable(gettext("default")), val: ko.observable('a')}}));
//    $('.error_arrow').remove();
//    $('input[type=text]').removeClass('error');
}

DW.change_question_type_for_selected_question = function (type_selector) {
    if (type_selector == "choice") {
        var old_type = questionnaireViewModel.selectedQuestion().type();
        if (old_type != 'select') {
            questionnaireViewModel.selectedQuestion().isAChoiceTypeQuestion("choice");
        }
    } else {
        questionnaireViewModel.selectedQuestion().type(type_selector);
    }
    questionnaireViewModel.selectedQuestion.valueHasMutated();
    questionnaireViewModel.questions.valueHasMutated();
}

DW.set_questionnaire_was_change = function () {
    if (!questionnaireViewModel.selectedQuestion().newly_added_question()) {
        DW.questionnaire_was_changed = true;
    }
}

$(document).ready(function () {
    var change_selector = "#range_min, #range_max, #max_length, [name=text_length], [name=date_format], #question_title";
    change_selector += ", [name=answers_possible], [name=type]";
    var click_selector = "#question-detail-panel .add_link";

    $(change_selector).change(DW.set_questionnaire_was_change);
    $(click_selector).click(DW.set_questionnaire_was_change);

    DW.has_submission_delete_warning = (function(){
        kwargs = {
                    container: "#submission_exists",
                    is_continue: false,
                    title: gettext('Warning: Your Collected Data Will be Lost'),
                    continue_handler: function(){
                        question = questionnaireViewModel.selectedQuestion();
                        questionnaireViewModel.removeQuestion(question);
                    }
                 };
        return new DW.warning_dialog(kwargs);
    }());


//    $("#questionnaire-code").change(function () {
//        if ($(this).val() != $("#saved-questionnaire-code").val()) {
//            DW.questionnaire_was_changed = true;
//        }
//    });
});


DW.has_questions_changed = function (existing_questions) {
    var new_question_codes = ko.utils.arrayMap(questionnaireViewModel.questions(), function (question) {
        return question.code();
    });
    var old_questions_codes = ko.utils.arrayMap(existing_questions, function (question) {
        return question.code;
    });
    return !_.isEqual(new_question_codes, old_questions_codes)
};

DW.addNewQuestion = function () {
    if(!questionnaireViewModel.validateSelectedQuestion())
        return;
    questionnaireViewModel.addQuestion();
    DW.close_the_tip_on_period_question();
    DW.smsPreview();
};


