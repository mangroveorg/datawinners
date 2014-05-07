DW.DataSenderQuestionnaire = function(){
    var self = this;

    self.name = DW.ko.createValidatableObservable();
    self.isWebEnabled = ko.observable(false);
    self.email = DW.ko.createValidatableObservable();
    self.telephone_number = DW.ko.createValidatableObservable();
    self.location = DW.ko.createValidatableObservable();
    self.geo_code = DW.ko.createValidatableObservable();
    self.short_code = DW.ko.createValidatableObservable();
    self.shouldGenerateUniqueId = DW.ko.createValidatableObservable({value: true});

    self._clearFields = function(){
        self.name("");
        self.isWebEnabled(false);
        self.email("");
        self.telephone_number("");
        self.location("");
        self.geo_code("");
        self.short_code("");
        self.shouldGenerateUniqueId(true);
    };

    self._clearFieldErrors = function(){
        self.name.clearError();
        self.email.clearError();
        self.telephone_number.clearError();
        self.location.clearError();
        self.geo_code.clearError();
        self.short_code.clearError();
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


    self.register = function(){
        $.blockUI({
            message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
            css: { width: '275px', top: '400px', left: '800px', zIndex: 1000000}
        });
        var data =  {
            name: self.name(),
            email: self.email(),
            telephone_number: self.telephone_number(),
            location: self.location(),
            geo_code: self.geo_code(),
            short_code: self.short_code(),
            //project id not present when registering datasenders from 'All DataSenders' page.
            project_id: (typeof project_id === 'undefined') ? "" : project_id
        };
        if(self.isWebEnabled()){
            data['devices'] = 'web';
        }

        $.ajax({
            type: 'POST',
            headers: { "X-CSRFToken": $.cookie('csrftoken')},
            url: register_datasender_url,
            data: data,
            dataType: 'json'
        }).done(function(response){
            $.unblockUI();
            if(response.success){
                self._clearFields();
                self._clearFieldErrors();
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