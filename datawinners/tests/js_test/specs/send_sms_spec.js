describe("Send A Message", function(){

    var model;

    beforeEach(function(){

        model = new SmsViewModel();

    });

    describe("Choose 'Send To' Option", function() {

        it("should disable send sms button until a valid send option is selected", function(){

            expect(model.disableSendSms()).toBe(true);

            model.selectedSmsOption("others");

            expect(model.disableSendSms()).toBe(false);
        });


        it("should show other contact section when other contacts option is selected", function() {

            expect(model.hideOtherContacts()).toBe(true);

            model.selectedSmsOption("others");

            expect(model.hideOtherContacts()).toBe(false);
        });


        it("should show list of questionnaires when contacts linked to questionnaire is selected", function() {

            expect(model.hideQuestionnaireSection()).toBe(true);

            model.selectedSmsOption("linked");

            expect(model.hideQuestionnaireSection()).toBe(false);
        });

    });

//    it("should give an error when text message is empty", function() {
//
//        expect(model.smsText.valid()).toBe(true);
//
//        model.selectedSmsOption("others");
//
//        expect(model.validate()).toBe(0);
//        expect(model.smsText.valid()).toBe(false);
//        expect(model.smsText.error()).toBe("This field is required.");
//
//    });


});
