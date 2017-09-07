var viewModel = function () {
    var self = this;
    this.fullName = DW.ko.createValidatableObservable({value: ""});
    this.email = DW.ko.createValidatableObservable({value: ""});
    this.title = DW.ko.createValidatableObservable({value: ""});
    this.mobilePhone = DW.ko.createValidatableObservable({value: ""});
    this.questionnaires = ko.observableArray([]);
    this.selectedQuestionnaires = ko.observableArray([]);
    this.role = DW.ko.createValidatableObservable({value: ""});
    this.hasFetchedQuestionnaires = ko.observable(false);
    this.addUserSuccess = ko.observable(false);
    this.hasFormChanged = ko.observable(false);
    this.showFlashMessage = ko.observable(false);
    this.flashMessage = ko.computed(function () {
        if (!self.addUserSuccess()) {
            return gettext("Sorry, the user registration failed due to a unknown system error, please try again.");
        }
        return gettext("User has been added successfully");
    });
    this.classFlashMessage = ko.computed(function (){
        return self.addUserSuccess() ? 'success-message-box' : 'message-box';
    });

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
        self.hasFormChanged(true);
    });

    this.role.subscribe(function () {
        self.hasFormChanged(true);
        self.role.setError(null);
    });

    this.title.subscribe(function(){
        if(!self.title() || self.title().length <= 100){
            self.title.setError(null);
        }
       self.hasFormChanged(true);
    });

    self.showSuccessMessage = function () {
        self.addUserSuccess(true);
        self.clearFields();
        self.showFlashMessage(true);
    }

    self.showErrorMessage = function () {
        self.showFlashMessage(true);
    }

    this.submit = function () {
        $.blockUI({
            message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
            css: {width: '275px'}
        });

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
        $.post('/account/user/new/', formData, function (response) {
            var responseJson = $.parseJSON(JSON.stringify(response));
            if (responseJson['add_user_success'] == true) {
                self.showSuccessMessage()
                $('html, body').animate({scrollTop: '0px'}, 0);
                DW.trackEvent('account-management', responseJson['current_user'] +'add-user', self.role());
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
        if (errors['title']) {
            self.title.setError(errors['title'][0]);
        }

        if ($.isEmptyObject(errors)) {
            self.showErrorMessage();
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
        this.fullName(null);
        this.email(null);
        this.email.setError(null);
        this.title(null);
        this.title.setError(null);
        this.role(null);
        this.mobilePhone(null);
        this.mobilePhone.setError(null);
        this.fullName.setError(null);
        this.questionnaires([]);
        this.hasFetchedQuestionnaires(false);
        this.selectedQuestionnaires([]);
        this.hasFormChanged(false);
        setTimeout(function () {
            self.addUserSuccess(false);
            self.showFlashMessage(false);
        }, 10000)
    };
    
    this.selectedQuestionnaireNames = function(){
    	var selectedQuestionairesObj = _.filter(self.questionnaires(),function(q){
    		return _.contains(self.selectedQuestionnaires(), q.id); 
    	});
    	var selectedQuestionnaireNames = _.map(selectedQuestionairesObj,function(q){
    		return q.name;
    	});
    	return selectedQuestionnaireNames;
    };
    
};

$(document).ready(function () {
    var userModel = new viewModel();
    window.userModel = userModel;
     if ($('#option_administrator')[0] === undefined) {
        userModel.role('Project Managers');
        userModel.fetchQuestionnaires();
    }
    userModel.hasFormChanged(false);
    ko.applyBindings(userModel, $("#user_profile_content")[0]);

    $('a[href]:visible').bind('click', function (event) {
        if(userModel.hasFormChanged()) {
            window.redirectUrl = $(this).attr('href');
            $("#form_changed_warning_dialog").dialog("open");
            return false;
        }
        return true;
    });

    window.addEventListener("beforeunload", function (e) {
        var confirmationMessage = "You have made changes to the form. ";
        confirmationMessage += "These changes will be lost if you navigate away from this page.";
        if (!userModel.hasFormChanged() || window.confirmationShown) {
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
        height: 150,
        width: 550
    };

    /*Aligning Add User Actions buttons towards right lane of input boxes*/
    var $userAction = $(".user_actions");
    var tableRowWidth = $(".administrative .tableRow").width(),
        userActionWidth = $userAction.width();

    $userAction.css("margin-left", (tableRowWidth - userActionWidth - 22) + "px");


    DW.delete_user_warning_dialog = new DW.warning_dialog(kwargs);
});
