function SmsViewModel(){
  var self = this;

  var smsTextArea = $("#sms-text");

  var project_id_to_send_sms = "";
  self.selectedSmsOption = ko.observable("");

  self.selectedSmsOption.subscribe(function(newSelectedSmsOption){
      self._resetErrorMessages();
      self.disableSendSms(newSelectedSmsOption == undefined );
  });


  self.sendButtonText = ko.observable(gettext("Send"));

  self.questionnairePlaceHolderText = ko.observable("");

  self.groupPlaceHolderText = ko.observable("");
  self.myPollRecipientsPlaceHolderText = ko.observable("");

  self.disableOtherContacts = ko.observable(false);

  self.hideQuestionnaireSection = ko.computed(function(){
      return this.selectedSmsOption() != 'linked';
  }, self);

  self.hideGroupSection = ko.computed(function(){
      return this.selectedSmsOption() != 'group';
  }, self);

  self.hideMyPollRecipientsSection = ko.computed(function(){
      return this.selectedSmsOption() != 'poll_recipients';
  }, self);


  self.showToSection = ko.observable(true);

  var questionnaireDetailsResponseHandler = function(response){
    var responseJson = $.parseJSON(response);
    var questionnaireItems = [];

    if(responseJson.length == 0){
        self.questionnairePlaceHolderText(gettext("Once you have created questionnaires, a list of your questionnaires will appear here."));
    }
    else{
       self.questionnairePlaceHolderText("");
    }

    $.each(responseJson, function(index, item){
        var checkBoxLabel = _.escape(item.name) + " <span class='grey italic'>" + item['ds-count'] + gettext(" recipients") + "</span>";
        questionnaireItems.push({value: item.id, label: checkBoxLabel, name: item.name});
    });

    if (is_poll){
        project_id_to_send_sms = project_id;
    }

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
        var itemNameEscaped = _.escape(item.name);
        var checkBoxLabel = itemNameEscaped + " <span class='grey italic'>" + item['count'] + gettext(" recipients") + "</span>";
        groupItems.push({value: item.name, label: checkBoxLabel, name: item.name});
    });
    if (is_poll){
        project_id_to_send_sms = project_id;
    }
    self.groupItems(groupItems);
  };

  var myRecipientsDetailsResponseHandler = function(response){
    var myRecipientsItems = [];
    if(Object.keys(response.my_poll_recipients).length == 0){
        self.myPollRecipientsPlaceHolderText(gettext("The list of your Poll Recipients is empty."));
    }
    else{
       self.myPollRecipientsPlaceHolderText("");
    }

    $.each(Object.keys(response.my_poll_recipients), function(index, item){

        var itemNameEscaped = _.escape(item);
        var checkBoxLabel = itemNameEscaped + " <span class='grey italic'>" + response.my_poll_recipients[item] + "</span>";
        myRecipientsItems.push({value: response.my_poll_recipients[item], label: checkBoxLabel, name: item});
    });
    if (is_poll){
        project_id_to_send_sms = project_id;
    }
    self.myPollRecipientsItems(myRecipientsItems);
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

    else if(selectedOption == 'poll_recipients' && self.myPollRecipientsItems().length == 0){
        self.myPollRecipientsPlaceHolderText(gettext("Loading..."));
        $.get(my_poll_recipients_count_url).done(myRecipientsDetailsResponseHandler);
    }
  });

  self.questionnaireItems = ko.observableArray([]);

  self.groupItems = ko.observableArray([]);
  self.myPollRecipientsItems = ko.observableArray([]);

  self.hideSpecifiedContacts = ko.observable(true);

  self.specifiedList = ko.observableArray([]);

  self.disableSendSms = ko.observable(true);

  self.sendToSpecificContacts = false;

  self.hideOtherContacts = ko.computed(function(){
      return this.selectedSmsOption() != 'others';
  }, self);

  self.smsText = DW.ko.createValidatableObservable({value: ""});

  self.smsCharacterCount = ko.observable(message_text.length + gettext(" of 160 characters used"));

  self.selectedQuestionnaireNames =  DW.ko.createValidatableObservable({value: []});

  self.selectedGroupNames =  DW.ko.createValidatableObservable({value: []});
  self.selectedMyPollRecipientsNames =  DW.ko.createValidatableObservable({value: []});

  self.smsOptionList = ko.observableArray([ {"label":gettext('Select Recipients'), disable: ko.observable(true)},
                                            {"label":gettext('Group'), "code": "group"},
                                            {"label":gettext('Contacts linked to a Questionnaire'), "code": "linked"},
                                            {"label":gettext('Other People'), "code": "others"}]);
  self.setOptionDisable= function(option, item) {
            ko.applyBindingsToNode(option, {disable: item.disable}, item);
    };

  self.smsSentSuccessful = ko.observable(false);

  self.othersList = DW.ko.createValidatableObservable({value: ""});

  self.specifiedListLengthText = ko.computed(function(){
      return this.othersList().split(", ").length + gettext(" Selected Contacts:");
  }, self);


  self.hideOtherSection = ko.computed(function(){
      return this.hideOtherContacts() || !this.hideSpecifiedContacts();
  }, self);

  self.clearSelection = function(){
    self.selectedSmsOption(undefined);
    smsTextArea.val("");
    self.questionnaireItems([]);
    self.disableOtherContacts(false);
    self.groupItems([]);
    self.myPollRecipientsItems([]);
    self.hideSpecifiedContacts(true);
    self.smsCharacterCount("0" + gettext(" of 160 characters used"));
    self.othersList("");
    self.selectedGroupNames([]);
    self.selectedQuestionnaireNames([]);
    self.selectedMyPollRecipientsNames([]);
    self._resetSuccessMessage();
    self._resetErrorMessages();
    self.showToSection(true);
    self.sendToSpecificContacts = false;
  };

  self.closeSmsDialog = function(){
    $("#send-sms-section").dialog('close');
    self.clearSelection();
    $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
    window.location.reload();
  };


  self.validateSmsText = function(){

    if(smsTextArea.val().trim() == ""){
        self.smsText.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.smsText.clearError();
        return true;
    }

  };

  var mobileNumberRegex = new RegExp('^\\+?[0-9]+$');

  self.validateOtherMobileNumbers = function(){

      if(self.selectedSmsOption() != 'others')
      {
          return true;
      }

      var successful = true;
      ko.utils.arrayForEach(self.othersList().split(","), function(item){
        if(!mobileNumberRegex.test(item.trim())){
            successful = false;
        }
      });

      if(!successful){
          self.othersList.setError(gettext("Please enter a valid phone number."));
          return false;
      }
      else{
          self.othersList.clearError();
          return true;
      }
  }

  self.validateOthersList = function(){

    if(self.selectedSmsOption() == 'others' && self.othersList() == ""){
        self.othersList.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.othersList.clearError();
        return self.validateOtherMobileNumbers();
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


  self.validateMyPollRecipientsSelection = function(){

    if(self.selectedSmsOption() == 'poll_recipients' && self.selectedMyPollRecipientsNames().length == 0){
        self.selectedMyPollRecipientsNames.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.selectedMyPollRecipientsNames.clearError();
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
    self.selectedMyPollRecipientsNames.clearError();
    self.selectedGroupNames.clearError();
    self.smsText.clearError();
    self.othersList.clearError();
  };

  self.validate = function(){
    return self.validateSmsText() & self.validateOthersList() & self.validateQuestionnaireSelection() & self.validateGroupSelection()  & self.validateMyPollRecipientsSelection();
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

  function _getReceipent(){
      if(self.sendToSpecificContacts && self.selectedSmsOption() == 'others'){
          return "specific-contacts";
      }
      else{
          return self.selectedSmsOption();
      }
  }
    ko.computed(function () {
        self.selectedSmsOption();
        self.selectedGroupNames();
        self.selectedMyPollRecipientsNames();
        self.selectedQuestionnaireNames();
        self._resetSuccessMessage();
        self._resetErrorMessages();
    })

    $("#sms-text").change(function(){
        self._resetSuccessMessage();
        self._resetErrorMessages();
    });

  self.sendSms = function(project_id){
      var project_id_type = typeof project_id;
      if (project_id_type != 'string') {
          project_id = "";
      }
      if(!self.validate()){
          return;
      }

      if (project_id == "" && project_id_to_send_sms != ""){
          project_id = project_id_to_send_sms;
      }
      self._resetSuccessMessage();
      self._resetErrorMessages();

      self.sendButtonText(gettext("Sending..."));
      self.disableSendSms(true);

      $.post(send_sms_url, {
          'sms-text': smsTextArea.val(),
          'others': self.othersList(),
          'recipient': _getReceipent(),
          'project_id': JSON.stringify(project_id),
          'questionnaire-names':  JSON.stringify(self.selectedQuestionnaireNames()),
          'group-names':  JSON.stringify(self.selectedGroupNames()),
          'my_poll_recipients':  JSON.stringify(self.selectedMyPollRecipientsNames()),
          'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
      }).done(function(response){

          var responseJson = $.parseJSON(response);
          self.sendButtonText(gettext("Send"));
          self.disableSendSms(false);
          if(responseJson.successful){
              $("#sms-success").removeClass("none");
              DW.trackEvent('send-sms-popup', 'send-sms-' + sms_popup_page, self.selectedSmsOption());
          }
          else {
              _showNoSMSCError(responseJson);
              _showFailedNumbersError(responseJson);
          }
      });
      //window.location.reload();
      $('html, body').animate({scrollTop: '0px'}, 0);
  };

}
