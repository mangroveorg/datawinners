describe("Send A Message", function(){

    var model;
    var smsTextArea;
    var successFlashMessage;
    var noSmscErrorMessage;
    var failedNumbersErrorMessage;

    beforeEach(function(){

        model = new SmsViewModel();
        smsTextArea = $("#sms-text");
        successFlashMessage = $("#sms-success");
        noSmscErrorMessage = $("#no-smsc");
        failedNumbersErrorMessage = $("#failed-numbers");
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

    describe("Validations for others selection", function(){

        it("should give a mandatory error when text message is empty", function() {

            smsTextArea.val("");
            model.selectedSmsOption("others");

            expect(model.validateSmsText()).toBe(false);

            expect(model.smsText.valid()).toBe(false);
            expect(model.smsText.error()).toBe("This field is required.");

        });

        it("should not give an error when text message is not empty", function() {

            smsTextArea.val("Some text");
            model.selectedSmsOption("others");

            expect(model.validateSmsText()).toBe(true);

            expect(model.smsText.valid()).toBe(true);
            expect(model.smsText.error()).toBe("");

        });

        it("should give a mandatory error when others contact list is empty", function() {

            model.othersList("");
            model.selectedSmsOption("others");

            expect(model.validateOthersList()).toBe(false);

            expect(model.othersList.valid()).toBe(false);
            expect(model.othersList.error()).toBe("This field is required.");

        });

        it("should not give an error when others contact list is not empty", function() {

            model.othersList("4785214");
            model.selectedSmsOption("others");

            expect(model.validateOthersList()).toBe(true);

            expect(model.othersList.valid()).toBe(true);
            expect(model.othersList.error()).toBe("");

        });


        it("should give an error when there is are mobile numbers with invalid mobile format", function() {

            model.othersList("4785214, +3838494000, string_which_should_fail");
            model.selectedSmsOption("others");

            expect(model.validateOthersList()).toBe(false);

            expect(model.othersList.valid()).toBe(false);
            expect(model.othersList.error()).toBe("Please enter a valid phone number.");

        });

         it("should not give an error when there is are mobile numbers with valid mobile format", function() {

            model.othersList("4785214, +3838494000, +9876543210, +012345678901234,  00000000000");
            model.selectedSmsOption("others");

            expect(model.validateOthersList()).toBe(true);

            expect(model.othersList.valid()).toBe(true);
            expect(model.othersList.error()).toBe("");

        });


    });

    describe("Validations for linked contacts selection", function(){

        it("should give a mandatory warning when linked contact list is empty", function() {

            model.selectedSmsOption("linked");
            model.selectedQuestionnaireNames([]);

            expect(model.validateQuestionnaireSelection()).toBe(false);

            expect(model.selectedQuestionnaireNames.valid()).toBe(false);
            expect(model.selectedQuestionnaireNames.error()).toBe("This field is required.");
        });

        it("should not give a warning when linked contact list is not empty", function() {

            model.selectedSmsOption("linked");
            model.selectedQuestionnaireNames(['some questionnaire']);

            expect(model.validateQuestionnaireSelection()).toBe(true);

            expect(model.selectedQuestionnaireNames.valid()).toBe(true);
            expect(model.selectedQuestionnaireNames.error()).toBe("");
        });

    });

    describe("Validations for group contacts selection", function(){

        it("should give a mandatory warning when group contact list is empty", function() {

            model.selectedSmsOption("group");
            model.selectedGroupNames([]);

            expect(model.validateGroupSelection()).toBe(false);

            expect(model.selectedGroupNames.valid()).toBe(false);
            expect(model.selectedGroupNames.error()).toBe("This field is required.");
        });

        it("should not give a warning when group contact list is not empty", function() {

            model.selectedSmsOption("group");
            model.selectedGroupNames(['group1']);

            expect(model.validateGroupSelection()).toBe(true);

            expect(model.selectedGroupNames.valid()).toBe(true);
            expect(model.selectedGroupNames.error()).toBe("");
        });

    });



    describe("Successful validations for SMS sending", function(){

        it("validation should be successful when all mandatory fields for the 'other' selection are specified", function(){

            model.selectedSmsOption("others");
            model.othersList("4785214");
            smsTextArea.val("Some text");

            expect(model.validate()).toBe(1);
        });


        it("validation should be successful when all mandatory fields for the 'linked contacts' selection are specified", function(){

            model.selectedSmsOption("linked");
            model.selectedQuestionnaireNames(['some questionnaire']);
            smsTextArea.val("some sms text");

            expect(model.validate()).toBe(1);
        });

    });


    it("should populate questionnaire name and contact count via ajax call", function(){

        spyOn(jQuery, "ajax").andCallFake(function() {
            expect(model.questionnairePlaceHolderText()).toBe("Loading...");
            var d = $.Deferred();
            d.resolve('[{"ds-count": 10, "name": "questionnaire_name", "id": "questionnaire1_id"}]');
            return d.promise();
        });

        model.questionnaireItems([]);

        model.selectedSmsOption("linked");

        expect($.ajax.mostRecentCall.args[0]["url"]).toEqual("http://example.com");
        expect($.ajax.mostRecentCall.args[0]["type"]).toEqual("get");
        expect(model.questionnairePlaceHolderText()).toBe("");
        expect(model.questionnaireItems()).toEqual([{'value': 'questionnaire1_id',
            label: "questionnaire_name <span class='grey italic'>10 recipients</span>", name: "questionnaire_name"}]);

    });

    it("should populate group name and contact count via ajax call", function(){

        spyOn(jQuery, "ajax").andCallFake(function() {
            expect(model.groupPlaceHolderText()).toBe("Loading...");
            var d = $.Deferred();
            d.resolve({"groups":[{"count": 10, "name": "group1"}, {"count": 20, "name": "group2"}]});
            return d.promise();
        });

        model.groupItems([]);

        model.selectedSmsOption("group");

        expect($.ajax.mostRecentCall.args[0]["url"]).toEqual("http://group-url.com");
        expect($.ajax.mostRecentCall.args[0]["type"]).toEqual("get");
        expect(model.groupPlaceHolderText()).toBe("");
        expect(model.groupItems()).toEqual([{'value': 'group1',
            label: "group1 <span class='grey italic'>10 recipients</span>", name: "group1"},
        {'value': 'group2',
            label: "group2 <span class='grey italic'>20 recipients</span>", name: "group2"}]);

    });



    it("should show message when no questionnaires defined", function(){

        spyOn(jQuery, "ajax").andCallFake(function() {
            expect(model.questionnairePlaceHolderText()).toBe("Loading...");
            var d = $.Deferred();
            d.resolve('[]');
            return d.promise();
        });

        model.questionnaireItems([]);
        model.selectedSmsOption("linked");

        expect($.ajax.mostRecentCall.args[0]["url"]).toEqual("http://example.com");
        expect($.ajax.mostRecentCall.args[0]["type"]).toEqual("get");
        expect(model.questionnairePlaceHolderText()).toBe("Once you have created questionnaires, a list of your questionnaires will appear here.");
        expect(model.questionnaireItems()).toEqual([]);

    });


    it("should show message when no groups defined", function(){

        spyOn(jQuery, "ajax").andCallFake(function() {
            expect(model.groupPlaceHolderText()).toBe("Loading...");
            var d = $.Deferred();
            d.resolve({"groups": []});
            return d.promise();
        });

        model.groupItems([]);
        model.selectedSmsOption("group");

        expect($.ajax.mostRecentCall.args[0]["url"]).toEqual("http://group-url.com");
        expect($.ajax.mostRecentCall.args[0]["type"]).toEqual("get");
        expect(model.groupPlaceHolderText()).toBe("Once you have created groups, a list of your groups will appear here.");
        expect(model.groupItems()).toEqual([]);

    });



    it("should post to server with correct sms data and show success flash message", function() {

        spyOn(jQuery, "ajax").andCallFake(function() {
            var d = $.Deferred();
            d.resolve('{"successful": true}');
            return d.promise();
        });

        successFlashMessage.addClass("success-message-box none");

        smsTextArea.val("some text");
        model.othersList("56363,2434");
        model.selectedSmsOption("others");
        model.selectedQuestionnaireNames(['random question']);

        model.sendSms();


        expect($.ajax.mostRecentCall.args[0]["type"]).toEqual("post");
        var requestBody = $.ajax.mostRecentCall.args[0].data;
        expect(requestBody.others).toEqual("56363,2434");
        expect(requestBody['sms-text']).toEqual("some text");
        expect(requestBody.recipient).toEqual("others");
        expect(requestBody['questionnaire-names']).toEqual('["random question"]');
        expect(requestBody['csrfmiddlewaretoken']).toEqual('csrf1234');

        expect(successFlashMessage.attr('class')).toEqual("success-message-box");
        expect(noSmscErrorMessage.attr('class')).toEqual("message-box none");
        expect(failedNumbersErrorMessage.attr('class')).toEqual("message-box none");

    });

    it("should show no smsc error when server sends 'no smsc' configured error ", function() {

        spyOn(jQuery, "ajax").andCallFake(function() {
            var d = $.Deferred();
            d.resolve('{"successful": false, "nosmsc": true}');
            return d.promise();
        });

        noSmscErrorMessage.addClass("message-box none");

        smsTextArea.val("some text");
        model.othersList("56363,2434");
        model.selectedSmsOption("others");
        model.selectedQuestionnaireNames(['random question']);

        model.sendSms();

        expect(noSmscErrorMessage.attr('class')).toEqual("message-box");
        expect(successFlashMessage.attr('class')).toEqual("success-message-box none");
    });


    it("should show failed numbers error when server sends failed numbers list ", function() {

        spyOn(jQuery, "ajax").andCallFake(function() {
            var d = $.Deferred();
            d.resolve('{"successful": false, "nosmsc": false, "failednumbers": ["8979878", "98798798"]}');
            return d.promise();
        });

        failedNumbersErrorMessage.addClass("message-box none");

        smsTextArea.val("some text");
        model.othersList("8979878,98798798");
        model.selectedSmsOption("others");
        model.selectedQuestionnaireNames(['random question']);

        model.sendSms();

        expect(failedNumbersErrorMessage.attr('class')).toEqual("message-box");
        expect(failedNumbersErrorMessage.text()).toEqual("failed numbers message: 8979878, 98798798.");
        expect(successFlashMessage.attr('class')).toEqual("success-message-box none");
    });

    it("should disable send sms when server post in progress", function(){

        spyOn(jQuery, "ajax").andCallFake(function() {
            expect(model.disableSendSms()).toBe(true);
            var d = $.Deferred();
            d.resolve('{"successful": false, "nosmsc": false, "failednumbers": ["8979878", "98798798"]}');
            return d.promise();
        });

        model.disableSendSms(false);

        smsTextArea.val("some text");
        model.othersList("8979878,98798798");
        model.selectedSmsOption("others");
        model.selectedQuestionnaireNames(['random question']);

        model.sendSms();

        expect(model.disableSendSms()).toBe(false);
    });


    it("should update send sms button text when server post in progress", function(){

        spyOn(jQuery, "ajax").andCallFake(function() {
            expect(model.sendButtonText()).toBe("Sending...");
            var d = $.Deferred();
            d.resolve('{"successful": false, "nosmsc": false, "failednumbers": ["8979878", "98798798"]}');
            return d.promise();
        });

        model.sendButtonText("Send");
        smsTextArea.val("some text");
        model.othersList("8979878,98798798");
        model.selectedSmsOption("others");
        model.selectedQuestionnaireNames(['random question']);

        model.sendSms();

        expect(model.sendButtonText()).toBe("Send");
    });

});
