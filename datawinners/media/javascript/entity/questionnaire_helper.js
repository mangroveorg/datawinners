//DW is the global name space for DataWinner
DW.init_inform_datasender_about_changes = function () {
    var kwargs = {container: "#inform_datasender_about_changes",
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
    var kwargs = {container: "#no_questions_exists", title: gettext('Warning: Empty questionnaire') };
    DW.empty_questionnaire_warning = new DW.warning_dialog(kwargs);
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
        display_choice['text'] = ko.observable(choice.text);
        display_choice['val'] = ko.observable(choice.val);
//        display_choice['id'] = choice.id;
        final_choices.push(DW.ko.createValidatableObservableObject({value: display_choice}));
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
            this.name = DW.ko.createValidatableObservable({value: q.name});
            this.title = DW.ko.createValidatableObservable({value: q.label});
        } else {
            this.title = DW.ko.createValidatableObservable({value: q.name});
        }

        this.code = ko.observable(q.code);
        this.type = ko.observable(q.type);
        this.is_entity_question = ko.observable(q.entity_question_flag);

        this.showDateFormats = ko.computed(function () {
            return this.type() == "date";
        }, this);

        this.showAddRange = ko.computed(function () {
            return this.type() == 'integer';
        }, this);

        this.showAddTextLength = ko.computed(function () {
            return this.type() == 'text' && !this.is_entity_question();
        }, this);

        this.required = ko.observable(q.required);

        this.answerType = DW.ko.createValidatableObservable();

        this.display = ko.computed(function () {
            return this.title();
        }, this);

        this.answerType.subscribe(function (selected_answer_type) {
            if (selected_answer_type === "") return;
            _clearErrors();
            DW.change_question_type_for_selected_question(selected_answer_type);
        }, this);

        var _clearErrors = function () {
            self.max_length.clearError();
            self.range_max.clearError();
            self.range_min.clearError();
            _clearChoiceErrors();
        };

        var initialValues = DW.initChoices(q.choices);
        this.choices = ko.observableArray(initialValues);

        this.choiceCanBeDeleted = ko.computed(function () {
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
                lastChoiceValue = DW.next_option_value(lastChoiceValue);
            }
            self.choices.remove(choice);
        };

        var _clearChoiceErrors = function () {
            ko.utils.arrayForEach(self.choices(), function (choice) {
                choice.clearError();
            });
        };

        var _validateChoice = function(choice){
            if (choice.value.text())
                choice.clearError();
            else
                choice.setError(gettext("This field is required."))
        };

        this.addOptionToQuestion = function () {
            var selectedQuestionCode = "a";
            var choiceText = "";
            if (this.choices().length > 0) {
                var lastChoice = this.choices()[this.choices().length - 1];
                selectedQuestionCode = DW.next_option_value(lastChoice.value.val());
            }
            else{
                choiceText = gettext("default");
            }
            var choiceItemText = ko.observable(choiceText);
            var choiceItem = DW.ko.createValidatableObservableObject({
                                                                        value: {
                                                                                    text: choiceItemText,
                                                                                    val: ko.observable(selectedQuestionCode)
                                                                               }
                                                                      });

            choiceItemText.subscribe(function(){
                _validateChoice(this);
            }, choiceItem);

            this.choices.push(choiceItem);

        };

        this.showAddChoice = function () {
            if (this.isAChoiceTypeQuestion() == "choice") {
                return true;
            }
            return false;
        };


        this.checkForQuestionnaireChange = function (choice) {
            if (_.any($(this.options.choices), function (v) {
                return v.val == choice.val;
            })) {
                DW.questionnaire_was_changed = true;
            }
        };

        this.date_format = ko.observable(q.date_format);
        this.length_limiter = ko.observable(q.length.max ? "length_limited" : "length_unlimited");

        this.showLengthLimiter = ko.computed(function () {
            return this.length_limiter() == 'length_limited';
        }, this);

        this.length_limiter.subscribe(function (new_length_limiter) {
            if (new_length_limiter == 'length_unlimited')
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
                    else if (this.range_min() == "" && !_.isNaN(parseInt(this.range_max()))) {
                        return $.sprintf(DW.instruction_template.max_number, this.range_max());
                    }
                    else if (this.range_max() == "" && !_.isNaN(parseInt(this.range_min()))) {
                        return $.sprintf(DW.instruction_template.min_number, this.range_min());
                    }
                    else if (!_.isNaN(parseInt(this.range_max())) && !_.isNaN(parseInt(this.range_min())) && this.range_max.valid())
                        return $.sprintf(DW.instruction_template.range_number, this.range_min(), this.range_max());
                    else
                        return DW.instruction_template.number;

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

        this.validate = function () {
            DW.ko.mandatoryValidator(this.title);
            DW.ko.mandatoryValidator(this.answerType);

            if (this.showLengthLimiter()) {
                DW.ko.mandatoryValidator(this.max_length);
                this.max_length.valid() && DW.ko.numericValidator(this.max_length);
            }

            else if (this.showAddRange()) {
                this.range_min() && DW.ko.numericValidator(this.range_min);
                this.range_max() && DW.ko.numericValidator(this.range_max);
                this._validateMinRangeIsLessThanMaxRange();
            }

            var isChoiceAnswerValid = true;
            if (this.showAddChoice()) {
                ko.utils.arrayForEach(this.choices(), function (choice) {
                    _validateChoice(choice)
                    isChoiceAnswerValid &= choice.valid();
                });
            }

            return this.title.valid() && this.answerType.valid() && this.max_length.valid()
                && this.range_min.valid() && this.range_max.valid() && isChoiceAnswerValid;
        };
        this._initializeObservableValidations();
    },

    _validateMinRangeIsLessThanMaxRange: function(){
        var min_range = parseInt(this.range_min());
        var max_range = parseInt(this.range_max());

        if(_.isNaN(min_range) || _.isNaN(max_range))
            return;

        if(min_range > max_range)
            this.range_max.setError(gettext("Max should be greater than min."));
        else
            this.range_max.clearError();
    },

    _initializeObservableValidations: function(){
       this.title.subscribe(function(){
          DW.ko.mandatoryValidator(this.title);
       }, this);

       this.max_length.subscribe(function(){
          DW.ko.mandatoryValidator(this.max_length);
          this.max_length.valid() && DW.ko.numericValidator(this.max_length);
       }, this);

       this.answerType.subscribe(function(){
          DW.ko.mandatoryValidator(this.answerType);
       }, this);

       this.range_min.subscribe(function(){
          DW.ko.numericValidator(this.range_min);
          this._validateMinRangeIsLessThanMaxRange();
       }, this);

       this.range_max.subscribe(function(){
          DW.ko.numericValidator(this.range_max);
          this._validateMinRangeIsLessThanMaxRange();
       }, this);


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
    questionnaireViewModel.selectedQuestion().addOptionToQuestion();
};

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
};

DW.set_questionnaire_was_change = function () {
    if (!questionnaireViewModel.selectedQuestion().newly_added_question()) {
        DW.questionnaire_was_changed = true;
    }
};

$(document).ready(function () {
    //TODO: Move to KO viewModel
    var change_selector = "#range_min, #range_max, #max_length, [name=text_length], [name=date_format], #question_title";
    change_selector += ", [name=answers_possible], [name=type]";

    $(document).on('change', change_selector, DW.set_questionnaire_was_change);
    //END

    DW.has_submission_delete_warning = (function () {
        var kwargs = {
                    container: "#submission_exists",
                    is_continue: false,
                    title: gettext('Warning: Your Collected Data Will be Lost'),
                    continue_handler: function(){
                        questionnaireViewModel.removeMarkedQuestion();
                    }
                 };
        return new DW.warning_dialog(kwargs);
    }());

});


DW.isQuestionsReOrdered = function (existing_questions) {
    var new_question_codes = ko.utils.arrayMap(questionnaireViewModel.questions(), function (question) {
        return question.code();
    });
    var old_questions_codes = ko.utils.arrayMap(existing_questions, function (question) {
        return question.code;
    });
    return !_.isEqual(new_question_codes, old_questions_codes)
};

DW.addNewQuestion = function () {
    if (!questionnaireViewModel.validateSelectedQuestion())
        return;
    questionnaireViewModel.addQuestion();
    DW.close_the_tip_on_period_question();
};

DW.templateDataCache = {};
DW.templateGroupingDataCache = null;

DW.getTemplateData = function (template_id) {
    var templateData = null;
    if (DW.templateDataCache[template_id] != undefined) {
        templateData = DW.templateDataCache[template_id];
    }
    else {
        $.ajax({
            type: 'GET',
            url: "/project/template/" + template_id,
            async: false,
            dataType: "json",
            success: function (data) {
                DW.templateDataCache[template_id] = data;
                templateData = data;
            }
        });
    }
    return templateData
};

DW.CancelQuestionnaireWarningDialog = function(options){
    var self = this;
    var successCallBack = options.successCallBack;
    var isQuestionnaireModified = options.isQuestionnaireModified;

    this.init = function(){
        self.cancelDialog = $("#cancel_questionnaire_warning_message");
        self.ignoreButton = self.cancelDialog.find(".no_button");
        self.saveButton = self.cancelDialog.find(".yes_button");
        self.cancelButton = self.cancelDialog.find("#cancel_dialog");
        _initializeDialog();
        _initializeIgnoreButtonHandler();
        _initializeCancelButtonHandler();
        _initializeSaveButtonHandler();
        _initializeLinkBindings();
    };

    var _initializeDialog = function(){
         self.cancelDialog.dialog({
            title:gettext("You Have Unsaved Changes"),
            modal:true,
            autoOpen:false,
            width:550,
            closeText:'hide'
        });
    };

    var _initializeIgnoreButtonHandler = function() {
        self.ignoreButton.bind('click', function(){
            self.cancelDialog.dialog("close");
            return _redirect();
        });
    };

    var _initializeCancelButtonHandler = function() {
         self.cancelButton.bind('click', function(){
            self.cancelDialog.dialog("close");
            return false;
         });
    };

    var _initializeSaveButtonHandler = function(){
        self.saveButton.bind('click', function(){
            if(questionnaireViewModel.validateSelectedQuestion() && questionnaireViewModel.validateQuestionnaireDetails())
            {
                successCallBack(function(){
                   return _redirect();
                });
            }
            self.cancelDialog.dialog("close");
        });
    };

    var _redirect = function() {
        window.location.href = redirect_url;
        return true;
    };

    var _initializeLinkBindings = function(){
        $("a[href]:visible, a#back_to_create_options, a#cancel_questionnaire").not(".add_link, .preview-navigation a, .sms_tester, .delete_project").bind('click', {self:this}, function (event) {
                var that = event.data.self;
                redirect_url = $(this).attr("href");
                if (isQuestionnaireModified()){
                    self.cancelDialog.dialog("open");
                    return false;
                }
                else
                    return _redirect();
        });
    };

};