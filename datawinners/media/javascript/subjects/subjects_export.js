$(document).ready(function () {
    $('#subject_export_link').click(function () {
        DW.trackEvent("unique-id", "unique-ids-exported");
        $("#query_text").val(($("#subjects_table_filter").find("input").val()));
        $("form[name='export_subjects']").submit();
    });
});
