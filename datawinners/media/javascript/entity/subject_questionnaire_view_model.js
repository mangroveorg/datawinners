var subjectQuestionnaireViewModel = {
    addQuestion:function () {
//        entity id question would be always the last question.
        var id_question = questionnaireViewModel.questions.pop();
        questionnaireViewModel.addQuestion();
        questionnaireViewModel.questions.push(id_question);
    },

    isTypeEnabled:function () {
        return true;
    }
};