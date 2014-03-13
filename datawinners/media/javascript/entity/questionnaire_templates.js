DW.templateDataCache = {};
DW.templateGroupingDataCache = null;

DW.getTemplateData = function (template_id) {
    var templateData = null;
    if (DW.templateDataCache[template_id] != undefined) {
        templateData = DW.templateDataCache[template_id];
    }
    else {
        $.ajax({
            type: 'GET',
            url: "/project/template/" + template_id,
            async: false,
            dataType: "json",
            success: function (data) {
                DW.templateDataCache[template_id] = data;
                templateData = data;
            }
        });
    }
    return templateData
};


DW.existingQuestionnaireCache = null;
DW.QuestionnaireDataCache = {};

DW.getQuestionnaireDataFromCache = function(questionnaireId){
    if(!DW.QuestionnaireDataCache[questionnaireId])
        return null;

    var questionnaireData = DW.QuestionnaireDataCache[questionnaireId];
    var existingQuestions = [];
    ko.utils.arrayForEach(questionnaireData.questions, function(question){
                    existingQuestions.push(question['label']);
                });
    return {
             'project_name': questionnaireData.name,
             'existing_questions': existingQuestions
           };
};