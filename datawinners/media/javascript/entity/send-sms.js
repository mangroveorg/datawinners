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

  self.showOtherContacts = ko.computed(function(){
      return this.selectedSmsOption() == 'Other People';
  }, self);

  self.smsText = ko.observable("");

  self.smsCharacterCount = ko.computed(function(){
      var length = this.smsText().length;
      return length + " of 160 characters used";
  }, self);

  self.smsOptionList = ko.observableArray(['Other People']);

  self.clearSelection = function(){
    self.selectedSmsOption("");
    self.smsText("");
  };

  self.closeSmsDialog = function(){
    $("#send-sms-section").dialog('close');
    self.clearSelection();
  };

  self.sendSms = function(){

  };

}
