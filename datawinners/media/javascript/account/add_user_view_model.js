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
    this.hasFormChanged = ko.observable(false);

    this.fullName.subscribe(function () {
        DW.ko.mandatoryValidator(self.fullName, 'This field is required');
        window.onbeforeunload = 'You have made some changes. Are you sure you want to discard the changes and move away?'
        self.hasFormChanged(true);
    });

    this.email.subscribe(function () {
        DW.ko.mandatoryValidator(self.email, 'This field is required')
        self.hasFormChanged(true);
    });

    this.mobilePhone.subscribe(function () {
        DW.ko.mandatoryValidator(self.mobilePhone, 'This field is required')
        self.hasFormChanged(true)
    });

    this.email.subscribe(function () {
        self.hasFormChanged(true);
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
        this.role('administrator');
        this.mobilePhone(null);
        this.mobilePhone.setError(null);
        this.fullName.setError(null);
        this.questionnaires([]);
        this.selectedQuestionnaires([]);
        this.hasFormChanged(false);
        setTimeout(function () {
            self.addUserSuccess(false);
        }, 4000)
    }
};

$(document).ready(function () {
    var userModel = new viewModel();
    window.userModel = userModel;
    ko.applyBindings(userModel, $("#add_user")[0]);

    window.addEventListener("beforeunload", function (e) {
        var confirmationMessage = 'It looks like you have been editing something. ';
        confirmationMessage += 'If you leave before saving, your changes will be lost.';
        var model = window.userModel;

        if (!model.hasFormChanged()) {
            return undefined;
        }

        (e || window.event).returnValue = confirmationMessage; //Gecko + IE
        return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
    });
});
