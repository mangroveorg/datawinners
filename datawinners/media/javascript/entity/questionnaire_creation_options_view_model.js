var questionnaireDataFetcher = new DW.QuestionnaireFetcher();
var templateFetcher = new DW.TemplateFetcher();
var questionnaireCreationOptionsViewModel = {
        selectedTemplateId: ko.observable(),
        showQuestionnaireCreationOptions: ko.observable(),
        templateData: ko.observable(),
        showAjaxLoader: ko.observable(),
        templateGroupingData: ko.observable(),
        existingQuestionnaires: ko.observable(),
        selectedQuestionnaire: ko.observable(),
        selectedQuestionnaireId: ko.observable(),
        selectedTemplate: ko.observable(),

        removeTemplateId: function () {
            questionnaireCreationOptionsViewModel.selectedTemplateId(null);
        },

        selectQuestionnaire: function(questionnaire){
            questionnaireCreationOptionsViewModel.selectedQuestionnaire(questionnaire.id);
            questionnaireCreationOptionsViewModel.selectedQuestionnaireId(questionnaire.id)
            questionnaireCreationOptionsViewModel.showAjaxLoader(true);
            var questionnaireData = questionnaireDataFetcher.getQuestionnaire(questionnaire.id);
            questionnaireCreationOptionsViewModel.templateData(questionnaireData);
            questionnaireCreationOptionsViewModel.selectedTemplateId(questionnaire.id);
            questionnaireCreationOptionsViewModel.showAjaxLoader(false);
        },

        chooseTemplate: function (template) {
            var templateId = template.id;
            questionnaireCreationOptionsViewModel.removeTemplateId();
            questionnaireCreationOptionsViewModel.showAjaxLoader(true);
            templateFetcher.getTemplateData(templateId).done(function(templateData){
               questionnaireCreationOptionsViewModel.showAjaxLoader(false);
               questionnaireCreationOptionsViewModel.templateData(templateData);
               questionnaireCreationOptionsViewModel.selectedTemplate({
                  projectName: templateData.project_name,
                  questions: templateData.existing_questions
               });
               questionnaireCreationOptionsViewModel.selectedTemplateId(templateId);
            });
        },

        getTemplates: function () {
            questionnaireCreationOptionsViewModel.removeTemplateId();
            templateFetcher.getTemplates().done(function(templates){
                  questionnaireCreationOptionsViewModel.templateGroupingData(templates);
            });
        },

        getExistingQuestionnaireList: function(){
           questionnaireDataFetcher.getExistingQuestionnaireList().done(function(questionnaireList){
               questionnaireCreationOptionsViewModel.existingQuestionnaires(questionnaireList);
            });
        },

        gotoQuestionnaireLoader: function (question_template_id) {
            location.hash = 'questionnaire/load/' + question_template_id;
        },

        setQuestionnaireCreationType: function () {
            var selectedOption = $('#questionnaire_types').accordion('option', 'active');
            if (selectedOption == 0) {
                location.hash = 'questionnaire/new';
            }
            else if (selectedOption == 2) {
                var question_template_id = questionnaireCreationOptionsViewModel.selectedTemplateId();
                questionnaireCreationOptionsViewModel.gotoQuestionnaireLoader(question_template_id);
            }
            else if(selectedOption == 1){
                location.hash = 'questionnaire/copy/' + questionnaireCreationOptionsViewModel.selectedTemplateId();
            }
        }
    };