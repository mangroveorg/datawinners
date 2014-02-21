whiteSpace = function (val) {
    var trimmed_value = $.trim(val);
    var list = trimmed_value.split(" ");
    return list.length <= 1;
};
var questionnaireViewModel =
{
    questions: ko.observableArray([]),
    hasAddedNewQuestions: false,
    hasDeletedOldQuestion: false,
    availableLanguages: [
        {name: 'English', code: 'en'},
        {name: 'French', code: 'fr'},
        {name: 'Malagasy', code: 'mg'}
    ],
    language: ko.observable(),
    projectName: ko.observable().extend({required: {params: true, message: gettext("This field is required.")}}),
    buttonShouldBeVisible: ko.observable(false),
    questionnaireCode: ko.observable().extend({required: {params: true, message: gettext("This field is required.")}})
        .extend({validation: {validator: whiteSpace,
            message: gettext("Space is not allowed in questionnaire code")}
        })
        .extend({pattern: {
            message: gettext("Only letters and digits are valid"),
            params: '^[A-Za-z0-9 ]+$'
        }}),

    questionnaireCreationType: ko.observable(),

    setQuestionnaireCreationType: function () {
        location.hash = 'new_questionnaire';
    },

    backToQuestionnaireCreationOptionsLink: function () {
        location.hash = '';
    },

    routing: Sammy(function () {
        this.get('#:new_questionnaire', function () {
            questionnaireViewModel.questionnaireCreationType(true);
        });
        this.get('create/$', function () {
            questionnaireViewModel.questionnaireCreationType(false);
        });
    }),


    addQuestion: function () {
        var question = new DW.question();
        question.display = ko.dependentObservable(function () {
            return this.title();
        }, question);
        question.newly_added_question(true);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.selectedQuestion(question);
        DW.init_question_constraints();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        DW.charCount();
        questionnaireViewModel.enableScrollToView(true);
        questionnaireViewModel.hasAddedNewQuestions = true;

    },
    loadQuestion: function (question) {
        question.display = ko.dependentObservable(function () {
            return this.title();
        }, question);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.questions.valueHasMutated();
    },

    renumberQuestions: function () {
        var questionPattern = /^Question \d+$/;
        for (var i = 0; i < questionnaireViewModel.questions().length; i++) {
            var question = questionnaireViewModel.questions()[i];
            if (questionPattern.test(question.title()))
                question.title("Question " + (i + 1));
        }
    },
    removeQuestion: function (question) {
        var index = $.inArray(question, questionnaireViewModel.questions());
        if (!question.newly_added_question()) {
            questionnaireViewModel.hasDeletedOldQuestion = true;
            DW.questionnaire_was_changed = true;
        }
        questionnaireViewModel.questions.remove(question);
        if (questionnaireViewModel.questions().length == 0) {
            questionnaireViewModel.selectedQuestion(new DW.question({is_null_question: true}));
            return;
        }
        questionnaireViewModel.renumberQuestions();
        if (question == questionnaireViewModel.selectedQuestion()) {
            var next_index = (index) % questionnaireViewModel.questions().length;
            questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
        }
        questionnaireViewModel.hasAddedNewQuestions = true;
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeIfQuestionIsSelectedQuestion: function (question) {
        if (questionnaireViewModel.selectedQuestion() == question) {
            questionnaireViewModel.removeQuestion(question);
        }
    },
    showAddChoice: function () {
        if (questionnaireViewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice") {
            if (questionnaireViewModel.selectedQuestion().choices().length == 0) {
                questionnaireViewModel.addOptionToQuestion();
                questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
            }
            return true;
        }
        return false;
    },
    showDateFormats: function () {
        return questionnaireViewModel.selectedQuestion().type() == "date";
    },
    showAddRange: function () {
        return questionnaireViewModel.selectedQuestion().type() == 'integer';
    },
    showAddTextLength: function () {
        return questionnaireViewModel.selectedQuestion().type() == 'text';
    },
    addOptionToQuestion: function () {
        var selectedQuestionCode = "a";
        if (questionnaireViewModel.selectedQuestion().choices().length > 0) {
            var lastChoice = questionnaireViewModel.selectedQuestion().choices()[questionnaireViewModel.selectedQuestion().choices().length - 1];
            selectedQuestionCode = DW.next_option_value(lastChoice.val);
        }
        questionnaireViewModel.selectedQuestion().choices.push({text: "", val: selectedQuestionCode});
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeOptionFromQuestion: function (choice) {
        questionnaireViewModel.checkForQuestionnaireChange(choice)
        var choices = questionnaireViewModel.selectedQuestion().choices();
        var indexOfChoice = $.inArray(choice, choices);
        var lastChoiceValue = choice['val'];
        var i = indexOfChoice + 1;
        for (i; i < choices.length; i = i + 1) {
            choices[i]['val'] = lastChoiceValue;
            $("span.bullet", $("#options_list li").eq(i)).html(lastChoiceValue + ".");
            lastChoiceValue = DW.next_option_value(lastChoiceValue);
        }
        questionnaireViewModel.selectedQuestion().choices.remove(choice);
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
    },
    selectedQuestion: ko.observable({}),
    changeSelectedQuestion: function (question) {
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        $(this).addClass("question_selected");
        DW.close_the_tip_on_period_question();
    },
    checkForQuestionnaireChange: function (choice) {
        var is_editing = typeof(is_edit) != 'undefined' && is_edit;
        if (is_editing && _.any($(questionnaireViewModel.selectedQuestion().options.choices), function (v) {
            return v.val == choice.val;
        })) {
            DW.questionnaire_was_changed = true;
        }
    },
    changeQuestionType: function (type_selector) {
        DW.init_question_constraints();
        DW.change_question_type_for_selected_question(type_selector.value);
    },
    showLengthLimiter: function () {
        return questionnaireViewModel.selectedQuestion().length_limiter() == 'length_limited';
    },
    set_all_questions_as_old_questions: function () {
        for (var question_index in questionnaireViewModel.questions()) {
            questionnaireViewModel.questions()[question_index].newly_added_question(false)
        }
    },
    has_newly_added_question: function () {
        return _.any($(questionnaireViewModel.questions()), function (v) {
            return v.newly_added_question();
        })
    },
    choiceCanBeDeleted: function () {
        return questionnaireViewModel.selectedQuestion().choices().length > 1 && questionnaireViewModel.isEnabled();
    },
    isEnabled: function () {
        if ($("#not_wizard").size() > 0) {
            return questionnaireViewModel.selectedQuestion().isEnabled();
        }
        else {
            return true;
        }
    },
    isTypeEnabled: function () {
        return questionnaireViewModel.isEnabled() && !questionnaireViewModel.selectedQuestion().event_time_field_flag();
    },
    moveQuestionUp: function (question) {
        var currentIndex = questionnaireViewModel.questions().indexOf(question);
        var questions = questionnaireViewModel.questions();
        if (currentIndex >= 1)
            questionnaireViewModel.questions.splice(currentIndex - 1, 2, questions[currentIndex], questions[currentIndex - 1]);
    },
    moveQuestionDown: function (question) {
        var currentIndex = questionnaireViewModel.questions().indexOf(question);
        var questions = questionnaireViewModel.questions();
        if (currentIndex < questions.length - 1)
            questionnaireViewModel.questions.splice(currentIndex, 2, questions[currentIndex + 1], questions[currentIndex]);
    },
    questionnaireHasErrors: ko.observable([]),

    errorInResponse: ko.observable(false),
    responseErrorMsg: ko.observable(),

    submit: function () {
        if (DW.questionnaire_form_validate()) {
            if (DW.has_questions_changed(DW.existing_questions)) {
                DW.questionnaire_was_changed = true;
            }
            if (is_edit && questionnaireViewModel.hasDeletedOldQuestion && !DW.has_submission_delete_warning.is_continue && DW.questionnaire_has_submission()) {
                DW.has_new_submission_delete_warning.show_warning();
            } else {
                $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
                DW.post_project_data('Test', function (response) {
                    return '/project/overview/' + response.project_id;
                });
            }
        }

    },

    saveAsDraft: function () {
        if (DW.questionnaire_form_validate()) {
            DW.post_project_data('Inactive', function (response) {
                return '/project/';
            });
        }
        return false;
    },

    enableScrollToView: ko.observable(false)
};
questionnaireViewModel.enableQuestionTitleFocus = ko.computed(function () {
    return questionnaireViewModel.enableScrollToView;
}, questionnaireViewModel);

questionnaireViewModel.isSelectedQuestionNull = ko.computed(function () {
    return this.selectedQuestion().isNullQuestion;
}, questionnaireViewModel);

