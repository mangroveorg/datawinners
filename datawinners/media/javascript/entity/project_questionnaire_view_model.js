function ProjectQuestionnaireViewModel() {
    var self = this;

    self.uniqueIdTypes = ko.observableArray([]);

    self.isUniqueIdTypeVisible = ko.observable(false);

    self.showUniqueIdTypes = function() {
        self.isUniqueIdTypeVisible(true);
    };

    self.selectUniqueIdType = function(uniqueIdType) {
        ProjectQuestionnaireViewModel.prototype.selectedQuestion().uniqueIdType(uniqueIdType);
        self.isUniqueIdTypeVisible(false);
    };

    self.newUniqueIdType = null;

    self.addNewUniqueIdType = function (){
        var newUniqueIdType = self.newUniqueIdType;
        $.post('/entity/type/create', {entity_type_regex: newUniqueIdType})
            .done(function (responseString) {
                var response = $.parseJSON(responseString);
                if (response.success) {
                    var array = self.uniqueIdTypes();
                    array.push(newUniqueIdType);
                    array.sort();
                    self.uniqueIdTypes.valueHasMutated();
                }
            });
    ;}
}

ProjectQuestionnaireViewModel.prototype = new QuestionnaireViewModel();
ProjectQuestionnaireViewModel.prototype.constructor = ProjectQuestionnaireViewModel;
