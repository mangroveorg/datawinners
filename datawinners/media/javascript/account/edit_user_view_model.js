var viewModel = function () {
    var self = this;
    this.fullName = DW.ko.createValidatableObservable({value: ""});
    this.email = DW.ko.createValidatableObservable({value: ""});
    this.title = DW.ko.createValidatableObservable({value: ""});
    this.mobilePhone = DW.ko.createValidatableObservable({value: ""});
    this.questionnaires = ko.observableArray([])
    this.selectedQuestionnaires = ko.observableArray([]);
    this.role = DW.ko.createValidatableObservable({value: "administrator"});
    this.editUserSuccess = ko.observable(false);
    this.hasFetchedQuestionnaires = ko.observable(false);
    this.hasFormChanged = ko.observable(false);
    this.userId = 0;

    this.fullName.subscribe(function () {
        DW.ko.mandatoryValidator(self.fullName, 'This field is required');
        self.hasFormChanged(true);
    });

    this.email.subscribe(function () {
        var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
        DW.ko.regexValidator(self.email, 'Invalid email id', re);
        self.hasFormChanged(true);
    });

    this.mobilePhone.subscribe(function () {
        var re = /^([0-9]{5,15})$/i;
        DW.ko.regexValidator(self.mobilePhone, 'Invalid phone number', re);
        self.hasFormChanged(true)
    });

    this.email.subscribe(function () {
        self.hasFormChanged(true);
    });

    this.selectedQuestionnaires.subscribe(function(){
        self.hasFormChanged(true);
    });

    this.role.subscribe(function(){
        self.hasFormChanged(true);
    });

    this.submit = function () {
        var formData = {
            'title': self.title(),
            'full_name': self.fullName(),
            'username': self.email(),
            'role': self.role(),
            'mobile_phone': self.mobilePhone(),
            'selected_questionnaires': self.selectedQuestionnaires() || [],
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        };
        $.post('/account/users/'  + self.userId + '/edit/', formData, function (response) {
            var responseJson = $.parseJSON(JSON.stringify(response));
            console.log("Response: "+ JSON.stringify(response));
            if (responseJson['edit_user_success'] == true) {
                self.editUserSuccess(true);
                self.clearFields();
                $('html, body').animate({scrollTop: '0px'}, 0);
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
        if (errors['full_name']) {
            self.fullName.setError(errors['full_name'][0]);
        }
    };

    this.fetchQuestionnaires = function () {
        if (self.role() == 'Project Managers') {
            $.getJSON('/entity/questionnairesandpolls/', {}, function (data) {
                $('#container_content').height('auto');
                self.hasFetchedQuestionnaires(true);
                self.questionnaires(data['questionnaires']);
            });
        }
        return true;
    };

    this.clearFields = function () {
        this.hasFormChanged(false);
        setTimeout(function () {
            self.editUserSuccess(false);
        }, 4000);
    }
};

$(document).ready(function () {
    var userModel = new viewModel();
    userModel.fullName(data_from_django['full_name']);
    userModel.email(data_from_django['username']);
    userModel.mobilePhone(data_from_django['mobile_phone']);
    userModel.title(data_from_django['title']);
    userModel.role(data_from_django['role']);
    userModel.userId = data_from_django['id'];
    var selectedQuestionnaires = [];
    data_from_django['questionnaires'].forEach(function (q) {
        selectedQuestionnaires.push(q.id);
    });
    userModel.fetchQuestionnaires();

    userModel.selectedQuestionnaires(selectedQuestionnaires);
    userModel.hasFormChanged = ko.observable(false);

    window.userModel = userModel;
    ko.applyBindings(userModel, $("#user_profile_content")[0]);

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
