var questionnaireViewModel =
{
    questions : ko.observableArray([]),
    hasAddedNewQuestions : false,
    hasDeletedOldQuestion : false,
    language:'en',

    addQuestion : function() {
        var question = new DW.question();
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        question.newly_added_question(true);
        questionnaireViewModel.remove_location_type();
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.selectedQuestion(question);
        DW.init_question_constraints();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        DW.charCount();
        questionnaireViewModel.enableScrollToView(true);
        questionnaireViewModel.hasAddedNewQuestions = true;

    },
    loadQuestion: function(question) {
        question.display = ko.dependentObservable(function() {
            return this.title();
        }, question);
        questionnaireViewModel.questions.push(question);
        questionnaireViewModel.questions.valueHasMutated();
    },

    renumberQuestions: function(){
        var questionPattern = /^Question \d+$/;
        for (var i = 0; i < questionnaireViewModel.questions().length; i++){
            var question = questionnaireViewModel.questions()[i];
            if (questionPattern.test(question.title()) )
                question.title("Question " + (i + 1));
        }
    },
    removeQuestion: function(question) {
        var index = $.inArray(question, questionnaireViewModel.questions());
        if (!question.newly_added_question()) {
            questionnaireViewModel.hasDeletedOldQuestion = true;
            DW.questionnaire_was_changed = true;
        }
        questionnaireViewModel.questions.remove(question);
        if(questionnaireViewModel.questions().length == 0){
            questionnaireViewModel.selectedQuestion(new DW.question({is_null_question: true}));
            return;
        }
        questionnaireViewModel.renumberQuestions();
        if (question == questionnaireViewModel.selectedQuestion()) {
            var next_index = (index) % questionnaireViewModel.questions().length;
            questionnaireViewModel.changeSelectedQuestion(questionnaireViewModel.questions()[next_index]);
        }
        questionnaireViewModel.hasAddedNewQuestions = true;
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeIfQuestionIsSelectedQuestion: function(question) {
        if (questionnaireViewModel.selectedQuestion() == question) {
            questionnaireViewModel.removeQuestion(question);
        }
    },
    showAddChoice:function() {
        if (questionnaireViewModel.selectedQuestion().isAChoiceTypeQuestion() == "choice") {
            if (questionnaireViewModel.selectedQuestion().choices().length == 0) {
                questionnaireViewModel.addOptionToQuestion();
                questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
            }
            return true;
        }
        return false;
    },
    showDateFormats:function() {
        return questionnaireViewModel.selectedQuestion().type() == "date";
    },
    showAddRange:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'integer';
    },
    showAddTextLength:function() {
        return questionnaireViewModel.selectedQuestion().type() == 'text';
    },
    addOptionToQuestion: function() {
        var selectedQuestionCode = "a";
        if (questionnaireViewModel.selectedQuestion().choices().length > 0) {
            var lastChoice = questionnaireViewModel.selectedQuestion().choices()[questionnaireViewModel.selectedQuestion().choices().length - 1];
            selectedQuestionCode = DW.next_option_value(lastChoice.val);
        }
        questionnaireViewModel.selectedQuestion().choices.push({text:"", val:selectedQuestionCode});
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
    },
    removeOptionFromQuestion:function(choice) {
        questionnaireViewModel.checkForQuestionnaireChange(choice)
        var choices = questionnaireViewModel.selectedQuestion().choices();
        var indexOfChoice = $.inArray(choice, choices);
        var lastChoiceValue = choice['val'];
        var i = indexOfChoice + 1;
        for(i; i < choices.length; i=i+1){
            choices[i]['val'] = lastChoiceValue;
            $("span.bullet", $("#options_list li").eq(i)).html(lastChoiceValue + ".");
            lastChoiceValue = DW.next_option_value(lastChoiceValue);
        }
        questionnaireViewModel.selectedQuestion().choices.remove(choice);
        questionnaireViewModel.selectedQuestion().choices.valueHasMutated();
        questionnaireViewModel.selectedQuestion.valueHasMutated();
    },
    selectedQuestion: ko.observable({}),
    changeSelectedQuestion: function(question) {
        questionnaireViewModel.selectedQuestion(question);
        questionnaireViewModel.selectedQuestion.valueHasMutated();
        questionnaireViewModel.questions.valueHasMutated();
        $(this).addClass("question_selected");
        DW.close_the_tip_on_period_question();
    },
    checkForQuestionnaireChange: function(choice){
        var is_editing = typeof(is_edit) != 'undefined' && is_edit;
        if(is_editing && _.any($(questionnaireViewModel.selectedQuestion().options.choices), function(v){return v.val == choice.val;})){
             DW.questionnaire_was_changed = true;
        }
    },
    changeQuestionType: function(type_selector) {
        DW.init_question_constraints();
        DW.change_question_type_for_selected_question(type_selector.value);
    },
    showLengthLimiter: function() {
        return questionnaireViewModel.selectedQuestion().length_limiter() == 'length_limited';
    },
    set_all_questions_as_old_questions:function(){
        for (var question_index in questionnaireViewModel.questions()){
            questionnaireViewModel.questions()[question_index].newly_added_question(false)
        }
    },
    has_newly_added_question:function(){
        return _.any($(questionnaireViewModel.questions()), function(v){return v.newly_added_question();})
    },
    choiceCanBeDeleted: function() {
        return questionnaireViewModel.selectedQuestion().choices().length > 1 && questionnaireViewModel.isEnabled();
    },
    isEnabled: function(){
        if($("#not_wizard").size() > 0){
            return questionnaireViewModel.selectedQuestion().isEnabled();
        }
        else{
            return true;
        }
    },
    isTypeEnabled: function(){
        return questionnaireViewModel.isEnabled() && !questionnaireViewModel.selectedQuestion().event_time_field_flag();
    },
    remove_location_type: function(){
        $(".question_type #location_type_input").hide();
    },
    moveQuestionUp: function(question){
        var currentIndex = questionnaireViewModel.questions().indexOf(question);
        var questions = questionnaireViewModel.questions();
        if(currentIndex >= 1)
            questionnaireViewModel.questions.splice(currentIndex-1, 2, questions[currentIndex], questions[currentIndex-1]);
    },
    moveQuestionDown: function(question){
        var currentIndex = questionnaireViewModel.questions().indexOf(question);
        var questions = questionnaireViewModel.questions();
        if(currentIndex < questions.length-1)
             questionnaireViewModel.questions.splice(currentIndex, 2, questions[currentIndex+1], questions[currentIndex]);
    },
    enableScrollToView: ko.observable(false)
};
questionnaireViewModel.enableQuestionTitleFocus = ko.computed(function(){
    return questionnaireViewModel.enableScrollToView;
},questionnaireViewModel);

questionnaireViewModel.isSelectedQuestionNull = ko.computed(function(){
        return this.selectedQuestion().isNullQuestion;
}, questionnaireViewModel);
