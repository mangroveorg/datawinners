function QuestionnaireViewModel(){
    var self = this;
    self.questions =  ko.observableArray([]);
    self.isEditMode = false;
    var questionToBeDeleted = null;
    self.hasExistingData = false;

    self.hasAddedNewQuestions =  false;
    self.hasDeletedOldQuestion = false;
    self.availableLanguages = [
        {name: 'English', code: 'en'},
        {name: 'French', code: 'fr'},
        {name: 'Malagasy', code: 'mg'},
        {name: 'Portuguese', code: 'pt'}
    ];

    self.language = ko.observable();
    self.projectName = DW.ko.createValidatableObservable();
    self.questionnaireCode = DW.ko.createValidatableObservable();
    self.isOpenSurvey = DW.ko.createValidatableObservable();

    self.showQuestionnaireForm = ko.observable();

    self.setQuestionToBeDeleted = function(question){
        questionToBeDeleted = question;
    };

    self.addQuestion = function () {
        var question = new DW.question();
        question.newly_added_question(true);
        self.questions.push(question);
        self.selectedQuestion(question);
        DW.init_question_constraints();
        DW.charCount();
        self.enableScrollToView(true);
        self.hasAddedNewQuestions = true;
    };

    self.loadQuestion = function (question) {
        self.questions.push(question);
    };

    self.removeMarkedQuestion = function() {
        self.removeQuestion(questionToBeDeleted);
    };

    //TODO: Verify usage
    self.removeIfQuestionIsSelectedQuestion = function(question) {
        if (self.selectedQuestion() == question) {
            self.removeQuestion(question);
        }
    },

    self.selectedQuestion = ko.observable();

    self.changeSelectedQuestion= function (question) {
        if(!self.validateSelectedQuestion())
            return;

        self.selectedQuestion(question);
        var questionType = self.selectedQuestion().isAChoiceTypeQuestion();
        if (questionType == 'none') questionType = self.selectedQuestion().type();
        self.selectedQuestion().answerType(questionType);

        $(this).addClass("question_selected");
        DW.close_the_tip_on_period_question();
        DW.show_completly_selected_question();
    };

    self.set_all_questions_as_old_questions= function () {
        for (var question_index=0; question_index < self.questions().length; question_index++) {
            self.questions()[question_index].newly_added_question(false)
        }
    };
    self.has_newly_added_question= function () {
        return _.any($(self.questions()), function (v) {
            return v.newly_added_question();
        })
    };

    //TODO:currently unused. re-look on introducing reporting period
    self.isTypeEnabled= function () {
        return !self.selectedQuestion().event_time_field_flag();
    };
    self.moveQuestionUp= function (question) {
        var currentIndex = self.questions().indexOf(question);
        var questions = self.questions();
        if (currentIndex >= 1)
            self.questions.splice(currentIndex - 1, 2, questions[currentIndex], questions[currentIndex - 1]);
    };
    self.moveQuestionDown= function (question) {
        var currentIndex = self.questions().indexOf(question);
        var questions = self.questions();
        if (currentIndex < questions.length - 1)
            self.questions.splice(currentIndex, 2, questions[currentIndex + 1], questions[currentIndex]);
    };

    self.enableQuestionnaireTitleFocus= ko.observable(false);
    self.questionHasErrors= ko.observable(false).extend({ notify: 'always' });

    self.errorInResponse= ko.observable(false);

    self.responseErrorMsg= ko.observable();

    self.enableScrollToView= ko.observable(false).extend({ notify: "always"});

    self.enableQuestionTitleFocus= ko.observable(false);

    self.clearQuestionnaire= function(){
        self.projectName(null);
        self.projectName.clearError();
        self.questions([]);
        self.errorInResponse(false);
        self.selectedQuestion(null);
    };

    self.validateSelectedQuestion= function(){
        if(!self.selectedQuestion())
        {
            self.questionHasErrors(false);
            return true;
        }

        var isValid = self.selectedQuestion().validate() && _validateSelectedQuestionHasUniqueTitle();
        self.questionHasErrors(!isValid);
        return isValid;
    };

    _validateSelectedQuestionHasUniqueTitle= function(){
        var selectedQuestion = self.selectedQuestion();
        var matchingQuestionsWithSameTitle = ko.utils.arrayFilter(self.questions(), function(question){
            return selectedQuestion.title().toLowerCase() == question.title().toLowerCase();
        });

        var isUnique = matchingQuestionsWithSameTitle.length == 1;
        if(!isUnique)
            selectedQuestion.title.setError(gettext("This question is a duplicate"));
        else
            selectedQuestion.title.clearError();

        return isUnique;
    };

    _validateQuestionnaireCode= function (questionnaireCode) {
        DW.ko.mandatoryValidator(questionnaireCode);
        questionnaireCode.valid() && DW.ko.alphaNumericValidator(questionnaireCode, true);
        if (questionnaireCode.valid()) {
            if (_isWhiteSpacesPresent(questionnaireCode()))
                questionnaireCode.setError(gettext("Space is not allowed in questionnaire code"));
            else
                questionnaireCode.clearError();
        }
    };

    self.validateQuestionnaireDetails= function(){
        DW.ko.mandatoryValidator(self.projectName);
        _validateQuestionnaireCode(self.questionnaireCode);

        var isValid = self.projectName.valid() && self.questionnaireCode.valid();
        self.enableQuestionnaireTitleFocus(!isValid);
        return isValid;
    };

    self.validateForSubmission= function(){
        return (self.questions().length > 0 && self.validateSelectedQuestion())
               & self.validateQuestionnaireDetails();
    }

    self.questionHasErrors.subscribe(function(questionHasErrors){
    questionHasErrors && this.enableQuestionTitleFocus(true);
    }, self);

    self.enableScrollToView.subscribe(function(enableScrollToView){
        enableScrollToView && this.enableQuestionTitleFocus(true);
    }, self);

    self.generateSmsPreview = ko.computed(function(){
        var smsPreviewString = this.questionnaireCode();
        _.each(this.questions(), function(question, index){
            smsPreviewString += " " + "answer" + (index + 1);
        });
        return smsPreviewString;
    }, self);


    self.projectName.subscribe(function(){
       DW.ko.mandatoryValidator(this.projectName);
    }, self);

    self.questionnaireCode.subscribe(function(){
       _validateQuestionnaireCode(this.questionnaireCode);
    }, self);


    _isWhiteSpacesPresent = function (val) {
        var trimmed_value = val.trim();
        var list = trimmed_value.split(" ");
        return list.length > 1;
    };

    self.getQuestionCodes = function(){
        return ko.utils.arrayMap(self.questions(), function (question) {
            return question.code();
        });
    };

};

QuestionnaireViewModel.prototype.validateAndRemoveQuestion = function(question){
        if (this.isEditMode && this.hasExistingData && !question.newly_added_question()) {
            this.setQuestionToBeDeleted(question);
            DW.has_submission_delete_warning.show_warning();
        }
        else{
            this.removeQuestion(question);
        }
};

QuestionnaireViewModel.prototype.removeQuestion = function(question) {
        if (!question.newly_added_question()) {
            this.hasDeletedOldQuestion = true;
            DW.questionnaire_was_changed = true;
        }
        this.questions.remove(question);
        if (question == this.selectedQuestion()) {
          this.selectedQuestion(null);
        }
        this.hasAddedNewQuestions = true;
};