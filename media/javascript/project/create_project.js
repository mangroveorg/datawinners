DW.init_view_model = function (question_list) {

    viewModel.questions([]);
    viewModel.questions.valueHasMutated();
    DW.current_code = 2;

    for (index in question_list) {
        var questions = new DW.question(question_list[index]);
        viewModel.loadQuestion(questions);
    }

    viewModel.selectedQuestion(viewModel.questions()[0]);
    viewModel.selectedQuestion.valueHasMutated();
};

$(document).ready(function() {
    DW.init_view_model(existing_questions);
    ko.applyBindings(viewModel);

    $($('input[name="frequency_enabled"]')).change(function() {
        if (this.value == "True") {
            $('#id_frequency_period').attr('disabled', false);
        }
        else {
            $('#id_frequency_period').attr('disabled', true);
        }
    });

    $($('input[name="activity_report"]')).change(function() {
        if (this.value == "no") {
            DW.init_view_model(subject_report_questions);
            $('#id_category').attr('disabled', false);
            $('#id_entity_type').attr('disabled', false);
        }
        else {
            DW.init_view_model(activity_report_questions);
            $('#id_category').attr('disabled', true);
            $('#id_entity_type').attr('disabled', true);
        }
    });
});