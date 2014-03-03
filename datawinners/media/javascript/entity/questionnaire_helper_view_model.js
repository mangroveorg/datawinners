var templateDataCache = {};
var questionnaireHelperModel = {
        selectedTemplateId: ko.observable(),
        showQuestionnaireCreationOptions: ko.observable(),
        templateData: ko.observable(),

        chooseTemplate: function (template) {
            var template_id = template.id;
            questionnaireHelperModel.selectedTemplateId(template_id);
            $.getJSON("/project/template/" + template_id, function (data) {
                questionnaireHelperModel.templateData(data);
            });
        },
        templateGroupingData: ko.observable(),
        getTemplates: function () {
            $.get("/project/templates", questionnaireHelperModel.templateGroupingData)
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