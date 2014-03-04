var questionnaireViewModel =
{
    questions: ko.observableArray([]),
    isEditMode: false,
    questionToBeDeleted: null,
    hasExistingData: false,

    hasAddedNewQuestions: false,
    hasDeletedOldQuestion: false,
    availableLanguages: [
        {name: 'English', code: 'en'},
        {name: 'French', code: 'fr'},
        {name: 'Malagasy', code: 'mg'}
    ],
    language: ko.observable(),
    projectName: DW.ko.createValidatableObservable(),
    questionnaireCode: DW.ko.createValidatableObservable(),

    showQuestionnaireForm: ko.observable(),

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

    removeMarkedQuestion:function() {
        questionnaireViewModel.removeQuestion(questionnaireViewModel.questionToBeDeleted);
    },

    removeQuestion: function (question) {
//        var index = $.inArray(question, questionnaireViewModel.questions());
        if (!question.newly_added_question()) {
            questionnaireViewModel.hasDeletedOldQuestion = true;
            DW.questionnaire_was_changed = true;
        }
        questionnaireViewModel.questions.remove(question);
        if (question == questionnaireViewModel.selectedQuestion()) {
          questionnaireViewModel.selectedQuestion(null);
        }
//        if (questionnaireViewModel.questions().length == 0) {
//            return;
//        }
//        if (question == questionnaireViewModel.selectedQuestion()) {
//            var next_index = (index) % questionnaireViewModel.questions().length;
//            questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
//        }
        questionnaireViewModel.hasAddedNewQuestions = true;
    },

    validateAndRemoveQuestion: function(question){
        if (questionnaireViewModel.isEditMode && questionnaireViewModel.hasExistingData && !question.newly_added_question()) {
            questionnaireViewModel.questionToBeDeleted = question;
            DW.has_submission_delete_warning.show_warning();
        }
        else
            questionnaireViewModel.removeQuestion(question);
    },

    //TODO: Verify usage
    removeIfQuestionIsSelectedQuestion: function (question) {
        if (questionnaireViewModel.selectedQuestion() == question) {
            questionnaireViewModel.removeQuestion(question);
        }
    },

    selectedQuestion: ko.observable(),

    changeSelectedQuestion: function (question) {
        if(!this.validateSelectedQuestion())
            return;
        questionnaireViewModel.selectedQuestion(question);
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

    //TODO:currently unused. re-look on introducing reporting period
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

    questionnaireHasErrors: ko.observable(false),

    errorInResponse: ko.observable(false),

    responseErrorMsg: ko.observable(),

    enableScrollToView: ko.observable(false),

    validateSelectedQuestion: function(){
        if(!this.selectedQuestion())
            return true;
        return this.selectedQuestion().validate() && this._validateSelectedQuestionHasUniqueTitle();
    },

    _validateSelectedQuestionHasUniqueTitle: function(){
        var selectedQuestion = this.selectedQuestion();
        var matchingQuestionsWithSameTitle = ko.utils.arrayFilter(this.questions(), function(question){
            return selectedQuestion.title().toLowerCase() == question.title().toLowerCase();
        });

        var isUnique = matchingQuestionsWithSameTitle.length == 1;
        if(!isUnique)
            selectedQuestion.title.setError(gettext("This question is duplicate"));
        else
            selectedQuestion.title.clearError();

        return isUnique;
    },

    _validateQuestionnaireCode: function () {
        var questionnaireCode = questionnaireViewModel.questionnaireCode;

        DW.ko.mandatoryValidator(questionnaireCode);
        questionnaireCode.valid() && DW.ko.alphaNumericValidator(questionnaireCode, true);
        if(questionnaireCode.valid()){
            if (DW.isWhiteSpacesPresent(questionnaireCode()))
                questionnaireCode.setError(gettext("Space is not allowed in questionnaire code"));
            else
                questionnaireCode.clearError();
        }
    },
    _validateQuestionnaireDetails: function(){
        DW.ko.mandatoryValidator(this.projectName);
        questionnaireViewModel._validateQuestionnaireCode();

        var isValid = questionnaireViewModel.projectName.valid() && questionnaireViewModel.questionnaireCode.valid();
        this.questionnaireHasErrors(!isValid);

        return isValid ;
    },
    selectedTemplateId : ko.observable(),
    templateQuestionsData: ko.observable(),

    chooseTemplate: function(template){
        questionnaireViewModel.selectedTemplateId(template.id);
        $.get("/project/template/"+template.id, questionnaireViewModel.templateQuestionsData)
    },
    templateQuestions: ko.computed(
        function(){
//            $.parseJSON(questionnaireViewModel.existing_questions)
        }
    ),
    templateGroupingData: ko.observable(),
    getTemplates: function(){
        $.get("/project/templates", questionnaireViewModel.templateGroupingData)
    },
    validateForSubmission: function(){
        return questionnaireViewModel.questions().length > 0 && questionnaireViewModel.validateSelectedQuestion()
               & questionnaireViewModel._validateQuestionnaireDetails();
    }

};
questionnaireViewModel.enableQuestionTitleFocus = ko.computed(function () {
    return questionnaireViewModel.enableScrollToView;
}, questionnaireViewModel);

questionnaireViewModel.generateSmsPreview = ko.computed(function(){
    var smsPreviewString = questionnaireViewModel.questionnaireCode();
    _.each(this.questions(), function(question, index){
        smsPreviewString += " " + "answer" + (index + 1);
    });
    return smsPreviewString;
}, questionnaireViewModel);


DW.isWhiteSpacesPresent = function (val) {
    var trimmed_value = val.trim();
    var list = trimmed_value.split(" ");
    return list.length > 1;
};

