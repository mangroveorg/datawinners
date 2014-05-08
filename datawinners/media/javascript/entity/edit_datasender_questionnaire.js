DW.EditDataSenderQuestionnaire = function(){
    var self = this;

    var _hasChanged = false;
    var dialog;

    var _closeParentDialog = function(){
        $("#datasender-popup").dialog('close');
    }

    var _initializeCancelDialog = function () {
        var dialogSection = $("#cancel_submission_warning_message");
        dialog = dialogSection.dialog({
            title:gettext("You Have Unsaved Changes"),
            modal:true,
            autoOpen:false,
            width:550,
            closeText:'hide'
        });
        dialogSection.find("a.no_button").on('click', function(){
            dialogSection.dialog("close");
        });
        dialogSection.find("a.yes_button").on('click', function(){
            dialogSection.dialog("close");
            _closeParentDialog();
        })
    };

    var _trackChanges = function(){
        _.each([self.name, self.telephone_number, self.location, self.geo_code], function(field){
             field.subscribe(function(){
                _hasChanged = true;
             });
        });
    };

    self.init = function(reporterDetails){
        self.name = DW.ko.createValidatableObservable({value: reporterDetails.name});
        self.email = DW.ko.createValidatableObservable({value: reporterDetails.email});
        self.telephone_number = DW.ko.createValidatableObservable({value: reporterDetails.phone_number});
        self.location = DW.ko.createValidatableObservable({value: reporterDetails.location});
        self.geo_code = DW.ko.createValidatableObservable({value: reporterDetails.geo_code});
        self.short_code = DW.ko.createValidatableObservable({value: reporterDetails.short_code});
        _initializeCancelDialog();
        _trackChanges();
    };

    self._clearFieldErrors = function(){
        self.name.clearError();
        self.telephone_number.clearError();
        self.location.clearError();
        self.geo_code.clearError();
    };

    var _showMessage = function(message, cssClass){
        $('#flash-message').text(message).addClass(cssClass).show().delay(4000).fadeOut(1000, function(){
                    $('#flash-message').hide();
        });
        DW.set_focus_on_flash_message();
    };

    var _showFlashSuccessMessage = function(message){
        _showMessage(message, 'success-message-box');
    };


    var _showFlashErrorMessage = function(message){
        _showMessage(message, 'message-box');
    };

    self.cancel = function(){
        if(_hasChanged){
            dialog.dialog("open");
        }
        else{
            _closeParentDialog();
        }
    };

    self.update = function(){
        $.blockUI({
            message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
            css: { width: '275px', top: '400px', left: '800px', zIndex: 1000000}
        });
        var data =  {
            name: self.name(),
            telephone_number: self.telephone_number(),
            location: self.location(),
            geo_code: self.geo_code()
        };

        $.ajax({
            type: 'POST',
            headers: { "X-CSRFToken": $.cookie('csrftoken')},
            url: edit_datasender_url,
            data: data,
            dataType: 'json'
        }).done(function(response){
            $.unblockUI();
            if(response.success){
                self._clearFieldErrors();
                _hasChanged = false;
                _showFlashSuccessMessage(response.message);
            }
            else{
                response.message && _showFlashErrorMessage(response.message);
                self._clearFieldErrors();
                _.each(response.errors, function(value, key){
                   self[key].setError(value);
                });
            }
        });
        return false;
    }

};