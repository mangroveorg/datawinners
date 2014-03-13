var questionnaireCreationOptionsViewModel = {
        selectedTemplateId: ko.observable(),
        showQuestionnaireCreationOptions: ko.observable(),
        templateData: ko.observable(),
        showAjaxLoader: ko.observable(),
        templateGroupingData: ko.observable(),
        existingQuestionnaires: ko.observable(),
        selectedQuestionnaire: ko.observable(),
        selectedQuestionnaireId: ko.observable(),

        removeTemplateId: function () {
            questionnaireCreationOptionsViewModel.selectedTemplateId(null);
        },

        selectQuestionnaire: function(questionnaire){
            questionnaireCreationOptionsViewModel.selectedQuestionnaire(questionnaire.id);
            questionnaireCreationOptionsViewModel.selectedQuestionnaireId(questionnaire.id)
            questionnaireCreationOptionsViewModel.showAjaxLoader(true);
            if(DW.QuestionnaireDataCache[questionnaire.id]){
                var questionnaireData = DW.getQuestionnaireDataFromCache(questionnaire.id);
                questionnaireCreationOptionsViewModel.templateData(questionnaireData);
            }
            else{
                $.ajax({
                        type: 'GET',
                        url: '/project/questionnaire/ajax/' + questionnaire.id,
                        dataType: "json",
                        async: false,
                        success: function (response) {
                            DW.QuestionnaireDataCache[questionnaire.id] = response;
                            var questionnaireData = DW.getQuestionnaireDataFromCache(questionnaire.id);
                            questionnaireCreationOptionsViewModel.templateData(questionnaireData);
                        }
                });

            }
            questionnaireCreationOptionsViewModel.selectedTemplateId(questionnaire.id);
            questionnaireCreationOptionsViewModel.showAjaxLoader(false);

        },

        chooseTemplate: function (template) {
            var template_id = template.id;
            questionnaireCreationOptionsViewModel.removeTemplateId();
            questionnaireCreationOptionsViewModel.showAjaxLoader(true);
            questionnaireCreationOptionsViewModel.templateData(DW.getTemplateData(template_id));
            questionnaireCreationOptionsViewModel.selectedTemplateId(template_id);
            questionnaireCreationOptionsViewModel.showAjaxLoader(false);
        },

        getTemplates: function () {
            questionnaireCreationOptionsViewModel.removeTemplateId();
            if (DW.templateGroupingDataCache) {
                questionnaireCreationOptionsViewModel.templateGroupingData(DW.templateGroupingDataCache);
            }
            else {
                    $.ajax({
                        type: 'GET',
                        url: project_templates_url,
                        dataType: "json",
                        success: function (data) {
                            DW.templateGroupingDataCache = data.categories;
                            questionnaireCreationOptionsViewModel.templateGroupingData(DW.templateGroupingDataCache);
                        }
                    });
            }
        },

        getExistingQuestionnaireList: function(){
            if(DW.existingQuestionnaireCache){
                questionnaireCreationOptionsViewModel.existingQuestionnaires(DW.existingQuestionnaireCache);
                return;
            }

            $.ajax({
                type: 'GET',
                url: existing_questionnaires_url,
                dataType: "json",
                success: function (response) {
                    DW.existingQuestionnaireCache = response.questionnaires;
                    questionnaireCreationOptionsViewModel.existingQuestionnaires(response.questionnaires);
                }
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