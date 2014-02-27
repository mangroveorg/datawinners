whiteSpace = function (val) {
    var trimmed_value = $.trim(val);
    var list = trimmed_value.split(" ");
    return list.length <= 1;
};
var questionnaireViewModel =
{
    questions: ko.observableArray([]),
    isEditMode: false,
    hasExistingData: false,

    hasAddedNewQuestions: false,
    hasDeletedOldQuestion: false,
    availableLanguages: [
        {name: 'English', code: 'en'},
        {name: 'French', code: 'fr'},
        {name: 'Malagasy', code: 'mg'}
    ],
    language: ko.observable(),
    projectName: ko.observable().extend({required: {params: true, message: gettext("This field is required.")}}),
    questionnaireCode: ko.observable().extend({
                                                required: {
                                                            params: true,
                                                            message: gettext("This field is required.")
                                                          }
                                              })
                              .extend({
                                        validation: {
                                                        validator: whiteSpace,
                                                        message: gettext("Space is not allowed in questionnaire code")}
                                                    })
                              .extend({
                                        pattern: {
                                                    message: gettext("Only letters and digits are valid"),
                                                    params: '^[A-Za-z0-9 ]+$'
                                                 }
                                      }),

    showQuestionnaireForm: ko.observable(),

    setQuestionnaireCreationType: function () {
        location.hash = 'questionnaire/new';
    },

    setQuestionnaireCreationTypeToEdit: function () {
        location.hash = 'questionnaire/edit';
    },

    backToQuestionnaireCreationOptionsLink: function () {
        location.hash = '';
    },

    addQuestion: function () {
        var question = new DW.question();
        question.newly_added_question(true);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.selectedQuestion(question);
        //TODO:verify and remove
        DW.init_question_constraints();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        DW.charCount();
        questionnaireViewModel.enableScrollToView(true);
        questionnaireViewModel.hasAddedNewQuestions = true;
    },

    loadQuestion: function (question) {
        questionnaireViewModel.questions.push(question);
    },

    removeQuestion: function (question) {
        var index = $.inArray(question, questionnaireViewModel.questions());
        if (!question.newly_added_question()) {
            questionnaireViewModel.hasDeletedOldQuestion = true;
            DW.questionnaire_was_changed = true;
        }
        questionnaireViewModel.questions.remove(question);
        if (questionnaireViewModel.questions().length == 0) {
            return;
        }
        if (question == questionnaireViewModel.selectedQuestion()) {
            var next_index = (index) % questionnaireViewModel.questions().length;
            questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
        }
        questionnaireViewModel.hasAddedNewQuestions = true;
        questionnaireViewModel.questions.valueHasMutated();
    },

    validateAndRemoveQuestion: function(question){
        if(this.isEditMode && this.hasExistingData && !question.newly_added_question())
            DW.has_submission_delete_warning.show_warning();
        else
            this.removeQuestion(question);
    },

    //TODO: Verify usage
    removeIfQuestionIsSelectedQuestion: function (question) {
        if (questionnaireViewModel.selectedQuestion() == question) {
            questionnaireViewModel.removeQuestion(question);
        }
    },

    selectedQuestion: ko.observable(),

    changeSelectedQuestion: function (question) {
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        var questionType = questionnaireViewModel.selectedQuestion().isAChoiceTypeQuestion();
        if (questionType == 'none') questionType = questionnaireViewModel.selectedQuestion().type();
        questionnaireViewModel.selectedQuestion().answerType(questionType);
        $(this).addClass("question_selected");
        DW.close_the_tip_on_period_question();
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

//    TODO: Check usages and remove
    isTypeEnabled: function () {
        return !questionnaireViewModel.selectedQuestion().event_time_field_flag();
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

    enableScrollToView: ko.observable(false)

};
questionnaireViewModel.enableQuestionTitleFocus = ko.computed(function () {
    return questionnaireViewModel.enableScrollToView;
}, questionnaireViewModel);



