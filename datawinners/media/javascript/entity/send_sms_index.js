$.valHooks.textarea = {
  get: function(elem){
      return elem.value.replace(/\r?\n/g, "\r\n");
  }
};


$(function(){

    var maxAllowedSMSCharacters = 160;

    var smsTextDialog = $("#send-sms-section");

    smsTextDialog.dialog({
        autoOpen: false,
        modal: true,
        title: gettext("Send an SMS"),
        zIndex: 700,
        width: 800,
        height: 'auto',
        close: function () {
            smsViewModel.clearSelection();
        }
    });

    $("#send_sms").on('click', function(){
        $("#send-sms-section").dialog('open');
    });

    var smsTextLengthCheck = function (e) {
        if (e.target.value.length > maxAllowedSMSCharacters) {
            $(this).val(e.target.value.substring(0, maxAllowedSMSCharacters));
        }

        smsViewModel.smsCharacterCount($(this).val().length + gettext(" of " + maxAllowedSMSCharacters + " characters used"));
    };

    var smsTextElement = $("#sms-text");

    smsTextElement.keyup(smsTextLengthCheck);

    smsTextElement.keypress(function (e) {
        var code = (e.keyCode ? e.keyCode : e.which);
        var enterKeyCode = 13;

        if(code == enterKeyCode && e.target.value.length + 2 > maxAllowedSMSCharacters){
            e.preventDefault();
            return false;
        }
        return true;
    });

    smsTextElement.keydown(smsTextLengthCheck);

    var smsViewModel = new SmsViewModel();
    window.smsViewModel = smsViewModel;

    ko.applyBindings(smsViewModel, smsTextDialog[0]);

});