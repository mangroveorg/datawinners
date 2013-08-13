$(document).ready(function () {
    $('#web_preivew').toggle();
    $('#subject_registration_preview').live('click', function (eventObject) {
        $('#wrapper_div_for_table').toggle();
        $('#web_preivew').toggle();
        $('.secondary_tab li:first').attr('class', 'inactive');
        $('.secondary_tab li:last').attr('class', 'active');
        eventObject.preventDefault();
    });

    $("table.styled_table thead input:checkbox").click(function (event) {
        self = event.target;
        $("table.styled_table tbody input:checkbox").attr('checked', $(self).is(":checked"));
    });

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
});
