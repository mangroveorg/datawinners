$(function(){

    $("#send-sms-section").dialog({
        autoOpen: false,
        modal: true,
        title: gettext("Send an SMS"),
        zIndex: 200,
        width: 800,
        height: 600,
        close: function () {
            smsViewModel.clearSelection();
        }
    });

    $("#send_sms").on('click', function(){
        $("#send-sms-section").dialog('open');
    });

    var smsViewModel = new SmsViewModel();
    window.model = smsViewModel;

    ko.applyBindings(smsViewModel, $("#send-sms-section")[0]);

});

function SmsViewModel(){
  var self = this;

  self.selectedSmsOption = ko.observable("");

  self.enableSendSms = ko.computed(function(){
      return this.selectedSmsOption() != undefined;
  }, self);

  self.showOtherContacts = ko.computed(function(){
      return this.selectedSmsOption() == 'Other People';
  }, self);

  self.smsText = DW.ko.createValidatableObservable({value: ""});

  self.smsCharacterCount = ko.computed(function(){
      var length = this.smsText().length;
      return length + " of 160 characters used";
  }, self);

  self.smsOptionList = ko.observableArray(['Other People']);

  self.smsSentSuccessful = ko.observable(false);

  self.othersList = DW.ko.createValidatableObservable({value: []});

  self.clearSelection = function(){
    self.selectedSmsOption("");
    self.smsText("");
    self.othersList([]);
    self._resetSuccessMessage();
    self._resetErrorMessages();
  };

  self.closeSmsDialog = function(){
    $("#send-sms-section").dialog('close');
    self.clearSelection();
  };


  self.validateSmsText = function(){

    if(self.smsText() == ""){
        self.smsText.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.smsText.clearError();
        return true;
    }

  };

  self.validateOthersList = function(){

    if(self.selectedSmsOption() == 'Other People' && self.othersList() == ""){
        self.othersList.setError(gettext("This field is required."));
        return false;
    }
    else{
        self.othersList.clearError();
        return true;
    }

  };

  self._resetSuccessMessage = function() {
    $("#sms-success").show().addClass("none");
  };

  self._resetErrorMessages = function() {
    $("#no-smsc").show().addClass("none");
    $("#failed-numbers").show().addClass("none");
  };

  self.validate = function(){
    return self.validateSmsText() && self.validateOthersList();
  };

  self.sendSms = function(){

      if(!self.validate()){
          return;
      }

      //remove inline style which gets added as part of flash-message
      self._resetSuccessMessage();
      self._resetErrorMessages();

      $.post(send_sms_url, {
          'sms-text': self.smsText(),
          'others': self.othersList(),
          'recipient': self.selectedSmsOption(),
          'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
      }).done(function(response){

          var response = $.parseJSON(response);
          if(response.successful){
              $("#sms-success").removeClass("none");
          }
          else {
              if (response.nosmsc) {
                  $("#no-smsc").removeClass("none");
              }
              else {
                  if (response.failednumbers) {
                      $("#failed-numbers").text(interpolate(gettext("failed numbers message: %(failed_numbers)s."), {"failed_numbers": response.failednumbers.join(", ")}, true));
                      $("#failed-numbers").removeClass("none");
                  }
              }
          }
      });
  };

}
