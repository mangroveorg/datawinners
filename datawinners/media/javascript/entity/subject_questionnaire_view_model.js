
var SubjectQuestionnaireViewModel = function(){
    var self = this;

    self.addQuestion =  function () {
        if (!self.validateSelectedQuestion())
            return;
//        entity id question would be always the last question.
        var id_question = self.questions.pop();

        self.removeLocationTypeOption();

        SubjectQuestionnaireViewModel.prototype.addQuestion();
        self.questions.push(id_question);
    };

    self.changeSelectedQuestion = function (question) {
        var locationTypeIndex = self.answerTypes.indexOf(self.locationType);
        if (question.newly_added_question()) {
            self.removeLocationTypeOption();
        }
        else {
            self.addLocationTypeOption();
        }
        SubjectQuestionnaireViewModel.prototype.changeSelectedQuestion(question);
    };

    self.locationType = {name: 'Location', value: 'list'};

    self.answerTypes = [
        {name: gettext('Select an Answer Type'), value: '', disable: true},
        {name: gettext('Word or Phrase'), value: 'text'},
        {name: gettext('Number'), value: 'integer'},
        {name: gettext('Date'), value: 'date'},
        {name: gettext('List of Choices'), value: 'choice'},
        {name: gettext('GPS Coordinates'), value: 'geocode'},
        {name: gettext('Telephone number'), value: 'telephone_number'}
    ];

    self.setOptionDisable = function(option, item) {
            ko.applyBindingsToNode(option, {disable: item.disable}, item);
    };

    self.removeLocationTypeOption = function() {
        var locationTypeIndex = self.answerTypes.indexOf(self.locationType);
        if (locationTypeIndex != -1) {
            self.answerTypes.splice(locationTypeIndex, 1)
        }
    };

    self.addLocationTypeOption = function() {
        var locationTypeIndex = self.answerTypes.indexOf(self.locationType);
        if (locationTypeIndex == -1) {
            self.answerTypes.splice(6, 0, self.locationType);
        }
    };

    //TODO: verify and remove
    self.isTypeEnabled = function() {
        return self.selectedQuestion().newly_added_question();
    };

};

SubjectQuestionnaireViewModel.prototype = new QuestionnaireViewModel();
SubjectQuestionnaireViewModel.prototype.constructor = SubjectQuestionnaireViewModel;