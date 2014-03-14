$(document).ready(
    function () {
        $('#questionnaire_types').accordion({
            header: '.questionnaire_type_header',
            autoHeight: false,
            collapsible: true,
            active: 100,
            change: function(event, ui){
                var activatedSection = $(event.target).accordion('option', 'active');
                questionnaireCreationOptionsViewModel.selectedCreationOption(activatedSection);
            }
        });
    }
);