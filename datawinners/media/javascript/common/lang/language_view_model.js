$(document).ready(function () {
    function LanguageViewModel() {
        var self = this;
        self.availableLanguages = languages;
        self.language = ko.observable();
        self.language_display = ko.computed(function(){
            return self.language();
        });
        self.customizedMessages = ko.observableArray();
        self.saveButtonText = ko.observable(gettext("Save"));
        self.initialState = ko.observable();
        self.isModified = ko.computed(function(){
            return self.initialState() != ko.toJSON(self.customizedMessages());
        },self);

        self.language.subscribe(function () {
            $.getJSON("/languages/custom_messages", {'language': languageViewModel.language()}).success(function (data) {
                var customized_messages = [];
                for (var i=0; i<data.length; i++) {
                    var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
                    var customized_message_item = { "code": data[i].code, "title": data[i].title, "message": messageItem };
                    messageItem.subscribe(function () {
                        DW.ko.mandatoryValidator(this.message, gettext("Enter reply SMS text."));
                    }, customized_message_item);
                    customized_messages.push(customized_message_item);
                }
                languageViewModel.customizedMessages(customized_messages);
                languageViewModel.initialState(ko.toJSON(languageViewModel.customizedMessages()))

            });
        }, self, 'change');
        self.language.subscribe(function(language_code){
            if(language_code && self.isModified()) {
                self.language(language_code);
                return false;
            }
        }, self, 'beforeChange');
        self.isValid=ko.computed(function(){
            var valid_fields = $.map(self.customizedMessages(), function(e){return e.message.valid()});
            return valid_fields.indexOf(false) == -1;
        }, self.customizedMessages);
        self.save = function (callback) {
            if (!self.isValid()) return;
            DW.loading();
            languageViewModel.saveButtonText(gettext("Saving..."));
            $.post('/languages/custom_messages', {
                    'data': JSON.stringify(ko.toJS(languageViewModel))},
                function (data) {
                    data = JSON.parse(data);
                    $(".save").text(gettext('Save'));
                    $('.success-message-box').text(data["message"]);
                    $('.success-message-box').show();
                    self.initialState(ko.toJSON(self.customizedMessages()));
                    if(typeof callback == "function") callback();
                }
            );

        };
    }



    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language);
    var options = {
        successCallBack:function(callback){
            languageViewModel.save(callback);
        },
        isQuestionnaireModified : function(){return languageViewModel.isModified();},
        cancelDialogDiv : "#cancel_language_changes_warning",
        validate: function(){
            return languageViewModel.isValid();
        }
    };
    new DW.CancelWarningDialog(options).init();

     $("#language").change(function(e){
        if(languageViewModel.isModified()) {
            e.preventDefault();

            var warning_dialog = new DW.CancelWarningDialog({
                cancelDialogDiv : "#cancel_language_changes_warning",
                cancelCallback:function(){$("#language option[value=" + languageViewModel.language() +"]").attr("selected","selected") ;},
                successCallBack:function(callback){   languageViewModel.save(callback);},
                actionCallback:function(){ languageViewModel.language($( "#language option:selected" ).val()); },
                validate: function(){ return languageViewModel.isValid(); }
        });
            warning_dialog.init();
            warning_dialog.show();
            return false;
        };
        DW.loading();
        languageViewModel.language($( "#language option:selected" ).val());
    });
});

