DW.TemplateFetcher = function(){
  var templateCache = {};
  var templateGroupingDataCache = null;

  this.getTemplateData = function (templateId) {
      var defd = $.Deferred();
         if (!templateCache[templateId]) {
            $.ajax({
                type: 'GET',
                url: "/project/template/" + templateId,
                dataType: "json"

            }).done(function (data) {
                    data['existing_questions'] = $.parseJSON(data['existing_questions']);
                    templateCache[templateId] = data;
                    defd.resolve(templateCache[templateId]);
            });
        }
        else{
            defd.resolve(templateCache[templateId]);
        }
        return defd.promise();
  };

  this.getTemplates = function(){
      var defd = $.Deferred();

      if(!templateGroupingDataCache){
          $.ajax({
                type: 'GET',
                url: project_templates_url,
                dataType: "json"
            }).done(function(response){
                  templateGroupingDataCache = response.categories;
                  defd.resolve(templateGroupingDataCache);
            });
      }
      else{
          defd.resolve(templateGroupingDataCache);
      }
      return defd.promise();
  };

};


DW.QuestionnaireFetcher = function(){
   var questionnaireCache = null;
   var questionnaireDataCache = {};

   this.getExistingQuestionnaireList = function(){
        var defd = $.Deferred();
        if (!questionnaireCache) {
                $.ajax({
                    type: 'GET',
                    url: existing_questionnaires_url,
                    dataType: "json"
                }).done(function (response) {
                    questionnaireCache = response.questionnaires;
                    defd.resolve(questionnaireCache);
                });
        }
        else{
            defd.resolve(questionnaireCache);
        }
        return defd.promise();
   };

   var _mapResponseToQuestions = function(questionnaireData){
        var existingQuestions = [];
        ko.utils.arrayForEach(questionnaireData.questions, function(question){
                    existingQuestions.push(question['label']);
                });

        return {
             'projectName': questionnaireData.name,
             'existingQuestions': existingQuestions
        };
   };

   this.getQuestionnaire = function(questionnaireId){
        var defd = $.Deferred();

        if(!questionnaireDataCache[questionnaireId])
        {
            $.ajax({
                        type: 'GET',
                        url: '/project/questionnaire/ajax/' + questionnaireId,
                        dataType: "json",
                        success: function (response) {
                            questionnaireDataCache[questionnaireId] = response;
                            defd.resolve(_mapResponseToQuestions(questionnaireDataCache[questionnaireId]));
                        }
            });
        }
        else{
            defd.resolve(_mapResponseToQuestions(questionnaireDataCache[questionnaireId]));
        }

        return defd.promise();
    };

    this.getQuestionnaireData = function(questionnaireId){
        return questionnaireDataCache[questionnaireId];
    };
};
