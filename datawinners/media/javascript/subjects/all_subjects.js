$(document).ready(function () {
    $('#web_preivew').toggle();
    $('#subject_registration_preview').live('click', function (eventObject) {
        $('#wrapper_div_for_table').toggle();
        $('#web_preivew').toggle();
        $('.secondary_tab li:first').attr('class', 'inactive');
        $('.secondary_tab li:last').attr('class', 'active');
        eventObject.preventDefault();
    });
});
