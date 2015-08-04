var viewModel = function () {
    var self = this;
    this.fullName = DW.ko.createValidatableObservable({value: ""});
    this.email = DW.ko.createValidatableObservable({value: ""});
    this.title = DW.ko.createValidatableObservable({value: ""});
    this.mobilePhone = DW.ko.createValidatableObservable({value: ""});
    this.questionnaires = ko.observableArray([])
    this.selectedQuestionnaires = ko.observableArray([]);
    this.role = DW.ko.createValidatableObservable({value: "administrator"});
    this.addUserSuccess = ko.observable(false);

    this.fullName.subscribe(function () {
        DW.ko.mandatoryValidator(self.fullName, 'This field is required')
    });

    this.email.subscribe(function () {
        DW.ko.mandatoryValidator(self.email, 'This field is required')
    });

    this.mobilePhone.subscribe(function () {
        DW.ko.mandatoryValidator(self.mobilePhone, 'This field is required')
    });

    this.submit = function () {
        var formData = {
            'title': self.title(),
            'full_name': self.fullName(),
            'username': self.email(),
            'role': self.role(),
            'mobile_phone': self.mobilePhone(),
            'selected_questionnaires': self.selectedQuestionnaires(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        };
        $.post('/account/user/new/', formData, function (response) {
            var responseJson = $.parseJSON(JSON.stringify(response));
            if (responseJson['add_user_success'] == true) {
                self.addUserSuccess(true);
                self.clearFields();
            } else {
                var errors = responseJson['errors'];
                self.parseErrors(errors);
            }
        });
    };

    this.parseErrors = function (errors) {
        if (errors['username']) {
            self.email.setError(errors['username'][0]);
        }
        if (errors['mobile_phone']) {
            self.mobilePhone.setError(errors['mobile_phone'][0]);
        }
    };

    this.fetchQuestionnaires = function () {
        if (self.role() == 'Project Managers') {
            $.getJSON('/entity/questionnaires/', {}, function (data) {
                $('#container_content').height('auto');
                self.questionnaires(data['questionnaires']);
            });
        }
        return true;
    };

    this.clearFields = function () {
        this.fullName(null);
        this.email(null);
        this.email.setError(null);
        this.title(null);
        this.mobilePhone(null);
        this.mobilePhone.setError(null);
        this.fullName.setError(null);
        this.questionnaires([]);
        this.selectedQuestionnaires([]);
        setTimeout(function () {
            self.addUserSuccess(false);
        }, 4000)
    }

};

$(document).ready(function () {
    var userModel = new viewModel();
    window.userModel = userModel;
    ko.applyBindings(userModel, $("#add_user")[0]);
});
