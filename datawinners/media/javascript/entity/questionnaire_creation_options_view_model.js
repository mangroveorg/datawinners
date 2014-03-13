var questionnaireCreationOptionsViewModel = {
        selectedTemplateId: ko.observable(),
        showQuestionnaireCreationOptions: ko.observable(),
        templateData: ko.observable(),
        showAjaxLoader: ko.observable(),
        removeTemplateId: function () {
            questionnaireCreationOptionsViewModel.selectedTemplateId(null);
        },
        chooseTemplate: function (template) {
            var template_id = template.id;
            questionnaireCreationOptionsViewModel.removeTemplateId();
            questionnaireCreationOptionsViewModel.showAjaxLoader(true);
            setTimeout(function(){
                questionnaireCreationOptionsViewModel.templateData(DW.getTemplateData(template_id));
                questionnaireCreationOptionsViewModel.selectedTemplateId(template_id);
                questionnaireCreationOptionsViewModel.showAjaxLoader(false);
            }, 0);
        },
        templateGroupingData: ko.observable(),
        getTemplates: function () {
            questionnaireCreationOptionsViewModel.removeTemplateId();
            setTimeout(function () {
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
                    })
                }
            }, 0);
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
                var question_template_id = questionnaireCreationOptionsViewModel.selectedTemplateId();
                questionnaireCreationOptionsViewModel.gotoQuestionnaireLoader(question_template_id);
            }
        }
    };