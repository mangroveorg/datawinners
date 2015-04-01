function SmsViewModel(){
  var self = this;

  var smsTextArea = $("#sms-text");

  self.selectedSmsOption = ko.observable("");

  self.selectedSmsOption.subscribe(function(newSelectedSmsOption){
      self._resetErrorMessages();
      self.disableSendSms(newSelectedSmsOption == undefined );
  });

  self.sendButtonText = ko.observable(gettext("Send"));

  self.questionnairePlaceHolderText = ko.observable("");

  self.groupPlaceHolderText = ko.observable("");

  self.hideQuestionnaireSection = ko.computed(function(){
      return this.selectedSmsOption() != 'linked';
  }, self);

  self.hideGroupSection = ko.computed(function(){
      return this.selectedSmsOption() != 'group';
  }, self);


  self.showToSection = ko.observable(true);

  var questionnaireDetailsResponseHandler = function(response){
    var response = $.parseJSON(response);
    var questionnaireItems = [];

    if(response.length == 0){
        self.questionnairePlaceHolderText(gettext("Once you have created Questionnaires, a list of your Questionnaires will appear here."));
    }
    else{
       self.questionnairePlaceHolderText("");
    }

    $.each(response, function(index, item){
        var checkBoxLabel = item.name + " <span class='grey italic'>" + item['ds-count'] + gettext(" recipients") + "</span>";
        questionnaireItems.push({value: item.id, label: checkBoxLabel, name: item.name});
    });

    self.questionnaireItems(questionnaireItems);
  };

  var groupDetailsResponseHandler = function(response){
    var groupItems = [];

    if(response.groups.length == 0){
        self.groupPlaceHolderText(gettext("Once you have created groups, a list of your groups will appear here."));
    }
    else{
       self.groupPlaceHolderText("");
    }

    $.each(response.groups, function(index, item){
        var checkBoxLabel = item.name + " <span class='grey italic'>" + item['count'] + gettext(" recipients") + "</span>";
        groupItems.push({value: item.name, label: checkBoxLabel, name: item.name});
    });

    self.groupItems(groupItems);
  };

  self.selectedSmsOption.subscribe(function(selectedOption){

    if(selectedOption == 'linked' && self.questionnaireItems().length == 0){
        self.questionnairePlaceHolderText(gettext("Loading..."));
        $.get(registered_ds_count_url).done(questionnaireDetailsResponseHandler);
    }
    else if(selectedOption == 'group' && self.groupItems().length == 0){
        self.groupPlaceHolderText(gettext("Loading..."));
        $.get(group_ds_count_url).done(groupDetailsResponseHandler);
    }
  });

  self.questionnaireItems = ko.observableArray([]);

  self.groupItems = ko.observableArray([]);

  self.disableSendSms = ko.observable(true);

  self.hideOtherContacts = ko.computed(function(){
      return this.selectedSmsOption() != 'others';
  }, self);

  self.smsText = DW.ko.createValidatableObservable({value: ""});

  self.smsCharacterCount = ko.observable("0" + gettext(" of 160 characters used"));

  self.selectedQuestionnaireNames =  DW.ko.createValidatableObservable({value: []});

  self.selectedGroupNames =  DW.ko.createValidatableObservable({value: []});

  self.smsOptionList = ko.observableArray([ {"label":gettext('Select Recipients'), disable: ko.observable(true)},
                                            {"label":gettext('Group'), "code": "group"},
                                            {"label":gettext('Contacts linked to a Questionnaire'), "code": "linked"},
                                            {"label":gettext('Other People'), "code": "others"}]);
  self.setOptionDisable= function(option, item) {
            ko.applyBindingsToNode(option, {disable: item.disable}, item);
    };

  self.smsSentSuccessful = ko.observable(false);

  self.othersList = DW.ko.createValidatableObservable({value: ""});

  self.clearSelection = function(){
    self.selectedSmsOption(undefined);
    smsTextArea.val("");
    self.questionnaireItems([]);
    self.groupItems([]);
    self.smsCharacterCount("0" + gettext(" of 160 characters used"));
    self.othersList("");
    self.selectedGroupNames([]);
    self.selectedQuestionnaireNames([]);
    self._resetSuccessMessage();
    self._resetErrorMessages();
    self.showToSection(true);
  };

  self.closeSmsDialog = function(){
    $("#send-sms-section").dialog('close');
    self.clearSelection();
  };


  self.validateSmsText = function(){

    if(smsTextArea.val() == ""){
        self.smsText.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.smsText.clearError();
        return true;
    }

  };

  self.validateOthersList = function(){

    if(self.selectedSmsOption() == 'others' && self.othersList() == ""){
        self.othersList.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.othersList.clearError();
        return true;
    }

  };

  self.validateQuestionnaireSelection = function(){

    if(self.selectedSmsOption() == 'linked' && self.selectedQuestionnaireNames().length == 0){
        self.selectedQuestionnaireNames.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.selectedQuestionnaireNames.clearError();
        return true;
    }

  };

  self.validateGroupSelection = function(){

    if(self.selectedSmsOption() == 'group' && self.selectedGroupNames().length == 0){
        self.selectedGroupNames.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.selectedGroupNames.clearError();
        return true;
    }

  };


  self._resetSuccessMessage = function() {
    $("#sms-success").show().addClass("none");
  };

  self._resetErrorMessages = function() {
    $("#no-smsc").show().addClass("none");
    $("#failed-numbers").show().addClass("none");
    self.selectedQuestionnaireNames.clearError();
    self.smsText.clearError();
    self.othersList.clearError();
  };

  self.validate = function(){
    return self.validateSmsText() & self.validateOthersList() & self.validateQuestionnaireSelection() & self.validateGroupSelection();
  };

  function _showFailedNumbersError(response) {
       if (response.failednumbers && !response.nosmsc) {
            $("#failed-numbers").text(interpolate(gettext("failed numbers message: %(failed_numbers)s."), {"failed_numbers": response.failednumbers.join(", ")}, true));
            $("#failed-numbers").removeClass("none");
       }
  }

  function _showNoSMSCError(response) {
        if (response.nosmsc) {
              $("#no-smsc").removeClass("none");
        }
  }


  self.sendSms = function(){

      if(!self.validate()){
          return;
      }

      self._resetSuccessMessage();
      self._resetErrorMessages();

      self.sendButtonText(gettext("Sending..."));
      self.disableSendSms(true);

      $.post(send_sms_url, {
          'sms-text': smsTextArea.val(),
          'others': self.othersList(),
          'recipient': self.selectedSmsOption(),
          'questionnaire-names':  JSON.stringify(self.selectedQuestionnaireNames()),
          'group-names':  JSON.stringify(self.selectedGroupNames()),
          'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
      }).done(function(response){

          var response = $.parseJSON(response);
          self.sendButtonText(gettext("Send"));
          self.disableSendSms(false);
          if(response.successful){
              $("#sms-success").removeClass("none");
          }
          else {
              _showNoSMSCError(response);
              _showFailedNumbersError(response);
          }
      });
  };

}
