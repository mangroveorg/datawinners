var questionnaireHelperModel = {
        selectedTemplateId: ko.observable(),
        showQuestionnaireCreationOptions: ko.observable(),
        templateData: ko.observable(),

        chooseTemplate: function (template) {
            var template_id = template.id;
            questionnaireHelperModel.selectedTemplateId(template_id);
            questionnaireHelperModel.templateData(DW.getTemplateDataFromCache(template_id));
        },

        templateGroupingData: ko.observable(),
        getTemplates: function () {
            questionnaireHelperModel.selectedTemplateId(null);
            questionnaireHelperModel.templateGroupingData(DW.getTemplateGroupingDataFromCache());
        },
        gotoQuestionnaireLoader: function (question_template_id) {
            location.hash = 'questionnaire/load/' + question_template_id;
        },
        setQuestionnaireCreationType: function () {
            var selectedOption = $('#questionnaire_types').accordion('option', 'active');
            if (selectedOption == 0) {
                location.hash = 'questionnaire/new';
            }
            else if (selectedOption == 1 || 2) {
                var question_template_id = questionnaireHelperModel.selectedTemplateId();
                questionnaireHelperModel.gotoQuestionnaireLoader(question_template_id);
            }
        }
    }
    ;