describe("Create a Poll Questionnaire", function(){

    it('should_show_send_sms_block_when_sms_option_is_selected', function(){
        window.smsViewModel = new SmsViewModel();
        var project_questionnaire_model = new ProjectQuestionnaireViewModel();

        project_questionnaire_model.show_sms('poll_via_sms');
        project_questionnaire_model.show_send_sms_block();
        expect(project_questionnaire_model.send_poll_sms()).toBe(true)

    });

    it('should_show_broadcast_block_when_broadcast_option_is_selected', function(){

        window.smsViewModel = new SmsViewModel();
        var project_questionnaire_model = new ProjectQuestionnaireViewModel();

        project_questionnaire_model.show_sms('poll_broadcast');
        project_questionnaire_model.show_send_sms_block();
        expect(project_questionnaire_model.send_broadcast()).toBe(true)

    });

     it('should_validate_poll_questionnaire_title', function(){
         window.smsViewModel = new SmsViewModel();
         var sms_view_model = window.smsViewModel;
         window.questionnaireViewModel = new ProjectQuestionnaireViewModel();
         var project_questionnaire_model = window.questionnaireViewModel;

         project_questionnaire_model.projectName("");
         project_questionnaire_model.send_broadcast(true);
         project_questionnaire_model.create_poll();
         expect(project_questionnaire_model.show_error()).toBe(true);
         expect(project_questionnaire_model.projectNameAlreadyExists()).toBe('This field is required');

    });

});