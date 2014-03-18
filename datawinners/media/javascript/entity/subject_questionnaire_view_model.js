var subjectQuestionnaireViewModel = {
    addQuestion: function () {
        if (!questionnaireViewModel.validateSelectedQuestion())
            return;
//        entity id question would be always the last question.
        var id_question = questionnaireViewModel.questions.pop();

        subjectQuestionnaireViewModel.removeLocationTypeOption();

        questionnaireViewModel.addQuestion();
        questionnaireViewModel.questions.push(id_question);
    },

    changeSelectedQuestion: function (question) {
        var locationTypeIndex = subjectQuestionnaireViewModel.answerTypes.indexOf(subjectQuestionnaireViewModel.locationType);
        if (question.newly_added_question()) {
            subjectQuestionnaireViewModel.removeLocationTypeOption();
        }
        else {
            subjectQuestionnaireViewModel.addLocationTypeOption();
        }
        questionnaireViewModel.changeSelectedQuestion(question);
    },

    locationType: {name: 'Location', value: 'list'},

    answerTypes: [
        {name: gettext('Select an Answer Type'), value: '', disable: true},
        {name: gettext('Word or Phrase'), value: 'text'},
        {name: gettext('Number'), value: 'integer'},
        {name: gettext('Date'), value: 'date'},
        {name: gettext('List of Choices'), value: 'choice'},
        {name: gettext('GPS Coordinates'), value: 'geocode'},
        {name: gettext('Telephone number'), value: 'telephone_number'}
    ],

    setOptionDisable: function(option, item) {
            ko.applyBindingsToNode(option, {disable: item.disable}, item);
    },

    removeLocationTypeOption: function () {
        var locationTypeIndex = subjectQuestionnaireViewModel.answerTypes.indexOf(subjectQuestionnaireViewModel.locationType);
        if (locationTypeIndex != -1) {
            subjectQuestionnaireViewModel.answerTypes.splice(locationTypeIndex, 1)
        }
    },

    addLocationTypeOption: function () {
        var locationTypeIndex = subjectQuestionnaireViewModel.answerTypes.indexOf(subjectQuestionnaireViewModel.locationType);
        if (locationTypeIndex == -1) {
            subjectQuestionnaireViewModel.answerTypes.splice(6, 0, subjectQuestionnaireViewModel.locationType);
        }
    },
    //TODO: verify and remove
    isTypeEnabled: function () {
        return questionnaireViewModel.selectedQuestion().newly_added_question();
    }
};