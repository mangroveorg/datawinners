function ProjectQuestionnaireViewModel() {
    var self = this;

    self.uniqueIdTypes = ko.observableArray(uniqueIdTypes);

    self.isUniqueIdTypeVisible = ko.observable(false);

    self.showUniqueIdTypes = function () {
        _clearNewUniqueIdError();
        self.isUniqueIdTypeVisible(true);
    };

    ko.postbox.subscribe("uniqueIdTypeSelected", _clearNewUniqueIdError, self);

    self.selectUniqueIdType = function (uniqueIdType) {
        ProjectQuestionnaireViewModel.prototype.selectedQuestion().uniqueIdType(uniqueIdType);
        self.isUniqueIdTypeVisible(false);
        _clearNewUniqueIdError();
    };

    self.newUniqueIdType = DW.ko.createValidatableObservable();

    self.addNewUniqueIdType = function () {
        var newUniqueIdType = self.newUniqueIdType();
        $.post('/entity/type/create', {entity_type_regex: newUniqueIdType})
            .done(function (responseString) {
                var response = $.parseJSON(responseString);
                if (response.success) {
                    var array = self.uniqueIdTypes();
                    array.push(newUniqueIdType);
                    array.sort();
                    self.newUniqueIdType.clearError();
                    self.uniqueIdTypes.valueHasMutated();
                }
                else {
                    self.newUniqueIdType.setError(response.message);
                }
            });
    };

    function _clearNewUniqueIdError() {
        self.newUniqueIdType("");
        self.newUniqueIdType.clearError();
    }

}

ProjectQuestionnaireViewModel.prototype = new QuestionnaireViewModel();
ProjectQuestionnaireViewModel.prototype.constructor = ProjectQuestionnaireViewModel;
