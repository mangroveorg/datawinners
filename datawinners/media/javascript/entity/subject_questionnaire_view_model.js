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
        {name: 'Select an Answer Type', value: ''},
        {name: 'Word or Phrase', value: 'text'},
        {name: 'Number', value: 'integer'},
        {name: 'Date', value: 'date'},
        {name: 'List of Choices', value: 'choice'},
        {name: 'GPS Coordinates', value: 'geocode'},
        {name: 'Telephone number', value: 'telephone_number'}
    ],

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