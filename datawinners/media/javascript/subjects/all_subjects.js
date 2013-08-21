$(document).ready(function () {

    $('#action li a').click(function (e) {
        if ($(this).parent().hasClass("disabled")) {
            e.preventDefault();
            return false;
        }
        var action = this.className;
        var ids = $.map($(".styled_table tbody input:checkbox:checked"), function (el, i) {
            return $(el).val()
        })
        if (action == "edit") {
            location.href = '/entity/subject/edit/' + subject_type.toLowerCase() + '/' + ids[0] + '/';
        } else {
            warnThenDeleteDialogBox(ids, subject_type.toLowerCase(), this);
        }

    });
    $('#subject_export_link').click(function () {
        $("#query_text").val(($("#subjects_table_filter").find("input").val()));
        $("form[name='export_subjects']").submit();
    });

});
