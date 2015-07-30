var viewModel = function() {
    var self = this;
    this.fullName = DW.ko.createValidatableObservable({value: ""});
    this.email = DW.ko.createValidatableObservable({value: ""});
    this.title = DW.ko.createValidatableObservable({value: ""});
    this.mobilePhone = DW.ko.createValidatableObservable({value: ""});
    this.questionnaires = ko.observableArray([])
    this.selectedQuestionnaires = ko.observableArray([]);
    this.role = DW.ko.createValidatableObservable({value: "administrator"});

    this.fullName.subscribe(function(){
       DW.ko.mandatoryValidator(self.fullName, 'This field is required')
    });

    this.email.subscribe(function(){
        DW.ko.mandatoryValidator(self.email, 'This field is required')
    });

    this.mobilePhone.subscribe(function(){
       DW.ko.mandatoryValidator(self.mobilePhone, 'This field is required')
    });

    this.submit = function() {
    };

    this.fetchQuestionnaires = function() {
        if(self.role()=='project-manager') {
            $.getJSON('/entity/questionnaires/', {}, function (data) {
                self.questionnaires(data['questionnaires']);
            });
        }
        return true;
    };
};

$(document).ready(function(){
    var userModel = new viewModel();
    window.userModel = userModel;
    ko.applyBindings(userModel, $("#add_user")[0]);
});