var viewModel = function () {
    var self = this;
    this.fullName = DW.ko.createValidatableObservable({value: ""});
    this.email = DW.ko.createValidatableObservable({value: ""});
    this.title = DW.ko.createValidatableObservable({value: ""});
    this.mobilePhone = DW.ko.createValidatableObservable({value: ""});
    this.questionnaires = ko.observableArray([]);
    this.selectedQuestionnaires = ko.observableArray([]);
    this.role = DW.ko.createValidatableObservable({value: "administrator"});
    this.editUserSuccess = ko.observable(false);
    this.questionnaireRevoked = ko.observable(false);
    this.hasFetchedQuestionnaires = ko.observable(false);
    this.hasFormEdited = ko.observable(false);
    this.userId = 0;
    this.hasEditedPermission = false;
    this.changedPermission = function(){
        return (this.hasEditedPermission) ? 'Permission-changed' : 'Permission-not-changed';
    }

    this.fullName.subscribe(function () {
        DW.ko.mandatoryValidator(self.fullName, 'This field is required');
        if(data_from_django['full_name'] != self.fullName()) {
            self.hasFormEdited(true);
        } else {
            self.hasFormEdited(false);
        }
    });

    this.email.subscribe(function () {
        var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
        DW.ko.regexValidator(self.email, 'Invalid email id', re);
        if(data_from_django['username'] != self.email()) {
            self.hasFormEdited(true);
        } else {
            self.hasFormEdited(false);
        }
    });

    this.mobilePhone.subscribe(function () {
        var re = /^([0-9]{5,15})$/i;
        DW.ko.regexValidator(self.mobilePhone, 'Invalid phone number', re);
        if(data_from_django['mobile_phone'] != self.mobilePhone()) {
            self.hasFormEdited(true);
        } else {
            self.hasFormEdited(false);
        }
    });

    this.title.subscribe(function() {
        if(data_from_django['title'] != self.title()) {
            self.hasFormEdited(true);
        } else {
            self.hasFormEdited(false);
        }
    });


    this.selectedQuestionnaires.subscribe(function(){

    });


    $(".questionnaire-list ul").click(function(event) {
        if(event.target.nodeName == "INPUT") {

            if(!$(event.target).is(":checked")) {
                self.questionnaireRevoked('True')
            }
            var questionnaires = $.map(data_from_django['questionnaires'], function(qstn) { return qstn.id; });

            if(userModel.fetchSelectedQuestions.length >= questionnaires.length) {
                $.map(userModel.fetchSelectedQuestions, function (qstn) {
                    if (questionnaires.indexOf(qstn) != -1) {
                        self.hasFormEdited(false);
                    } else {
                        self.hasFormEdited(true);
                        self.hasEditedPermission = true;
                    }
                });
            } else {
                self.hasFormEdited(true);
                self.hasEditedPermission = true;
            }
        }
    });

    this.role.subscribe(function(){
        if(data_from_django['role'] != self.role()) {
            self.hasFormEdited(true);
        } else {
            self.hasFormEdited(false);
        }
    });

    this.submit = function () {
        $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
        
        var formData = {
            'title': self.title(),
            'full_name': self.fullName(),
            'username': self.email(),
            'role': self.role(),
            'mobile_phone': self.mobilePhone(),
            'selected_questionnaires': self.selectedQuestionnaires() || [],
            'selected_questionnaire_names': self.selectedQuestionnaireNames() || [],
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        };
        $.post('/account/users/'  + self.userId + '/edit/', formData, function (response) {
            var responseJson = $.parseJSON(JSON.stringify(response));
            if (responseJson['edit_user_success'] == true) {
                self.editUserSuccess(true);
                self.clearFields();
                $('html, body').animate({scrollTop: '0px'}, 0);
                DW.trackEvent('account-management', 'edit-user', self.changedPermission());
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
        if (errors['role']) {
            self.role.setError(errors['role'][0]);
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
        this.hasFormEdited(false);
        self.questionnaireRevoked(false);
        setTimeout(function () {
            self.editUserSuccess(false);
        }, 10000);
    };
    
    this.selectedQuestionnaireNames = function(){
    	var selectedQuestionairesObj = _.filter(self.questionnaires(),function(q){
    		return _.contains(self.selectedQuestionnaires(), q.id); 
    	});
    	var selectedQuestionnaireNames = _.map(selectedQuestionairesObj,function(q){
    		return q.name;
    	});
    	return selectedQuestionnaireNames;
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
    userModel.fetchSelectedQuestions = selectedQuestionnaires;

    userModel.selectedQuestionnaires(selectedQuestionnaires);

    window.userModel = userModel;
    ko.applyBindings(userModel, $("#user_profile_content")[0]);

    $('a[href]:visible').bind('click', function (event) {
        if(userModel.hasFormEdited()) {
            window.redirectUrl = $(this).attr('href');
            $("#form_changed_warning_dialog").dialog("open");
            return false;
        }
        return true;
    });

    window.addEventListener("beforeunload", function (e) {
        var confirmationMessage = "You have made changes to the form. ";
        confirmationMessage += "These changes will be lost if you navigate away from this page.";
        if (!userModel.hasFormEdited() || window.confirmationShown) {
            return undefined;
        }

        (e || window.event).returnValue = confirmationMessage; //Gecko + IE
        return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
    });

    var kwargs = {
        container: "#form_changed_warning_dialog",
        continue_handler: function () {
            window.confirmationShown = true;
            window.location.href = window.redirectUrl;
        },
        title: gettext("Your change(s) will be lost"),
        cancel_handler: function () {
        },
        height: 160,
        width: 550
    };

    /*Aligning Edit User Actions buttons towards right lane of input boxes*/
    var $editUser = $(".edit_user_actions");
    var tableRowWidth = $(".administrative .tableRow").width(),
        editUserActionWidth = $editUser.width();

    $editUser.css("margin-left", (tableRowWidth - editUserActionWidth - 22) + "px");


    DW.delete_user_warning_dialog = new DW.warning_dialog(kwargs);

});
