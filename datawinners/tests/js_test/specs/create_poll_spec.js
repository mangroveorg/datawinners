describe("Create a Poll Questionnaire", function(){

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