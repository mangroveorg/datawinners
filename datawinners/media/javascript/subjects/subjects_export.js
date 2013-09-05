$(document).ready(function () {
    $('#subject_export_link').click(function () {
        $("#query_text").val(($("#subjects_table_filter").find("input").val()));
        $("form[name='export_subjects']").submit();
    });
});
