var questionnaireDataFetcher = new DW.QuestionnaireFetcher();
var templateFetcher = new DW.TemplateFetcher();

var questionnaireCreationOptionsViewModel = {
        selectedTemplateId: ko.observable(),
        showQuestionnaireCreationOptions: ko.observable(),
        selectedQuestionnaire: ko.observable(),
        showAjaxLoader: ko.observable(),
        templateGroupingData: ko.observable(),
        existingQuestionnaires: ko.observable(),
        selectedQuestionnaireId: ko.observable(),
        selectedTemplate: ko.observable(),
        selectedCreationOption: ko.observable(100), //don't select any option by default

        resetCreationOption: function(){
          questionnaireCreationOptionsViewModel.selectedCreationOption(100);
        },

        removeTemplateId: function () {
            questionnaireCreationOptionsViewModel.selectedTemplateId(null);
        },

        selectQuestionnaire: function(questionnaire){
            var questionnaire_id = questionnaire.id;
            var that = questionnaireCreationOptionsViewModel;
            that.selectedQuestionnaireId(null);
            that.showAjaxLoader(true);
            questionnaireDataFetcher.getQuestionnaire(questionnaire_id).done(function(questionnaireData){
                that.showAjaxLoader(false);
                that.selectedQuestionnaire(questionnaireData);
                that.selectedQuestionnaireId(questionnaire_id);
            });

        },

        chooseTemplate: function (template) {
            var that = questionnaireCreationOptionsViewModel;
            var templateId = template.id;
            that.removeTemplateId();
            that.showAjaxLoader(true);
            templateFetcher.getTemplateData(templateId).done(function(templateData){
               that.showAjaxLoader(false);
               that.selectedTemplate({
                  projectName: templateData.project_name,
                  questions: templateData.existing_questions
               });
               that.selectedTemplateId(templateId);
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

        setQuestionnaireCreationType: function () {
            var that = questionnaireCreationOptionsViewModel;
            var selectedOption = that.selectedCreationOption();
            if (selectedOption == 0) {
                location.hash = 'questionnaire/new';
            }
            else if (selectedOption == 2) {
                location.hash = 'questionnaire/load/' + that.selectedTemplateId();
            }
            else if(selectedOption == 1){
                location.hash = 'questionnaire/copy/' + that.selectedQuestionnaireId();
            }
        }
    };

    questionnaireCreationOptionsViewModel.isContinueVisible = ko.computed(function(){
        var creationOption = this.selectedCreationOption();
        if(creationOption === false)
            return false;
        if(creationOption == 0)
            return true;
        if(creationOption == 1 && this.selectedQuestionnaireId())
            return true;
        if(creationOption == 2 && this.selectedTemplateId())
            return true;
        return false;
    }, questionnaireCreationOptionsViewModel);

    questionnaireCreationOptionsViewModel.selectedCreationOption.subscribe(function(){
        this.selectedQuestionnaireId(null);
    }, questionnaireCreationOptionsViewModel);