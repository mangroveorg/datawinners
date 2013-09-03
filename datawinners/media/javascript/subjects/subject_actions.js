DW = DW || {};

DW.SubjectPagination = function () {

    this.deactivate_select_across_pages = function () {
        $("#select_all_message").remove();
        $('#select_all_link').removeClass('selected');
    };

    this.display_select_across_pages_message = function (no_of_records_on_page, total_number_of_records) {
        if (no_of_records_on_page != total_number_of_records) {
            var select_all_text = interpolate(gettext("Select all <b> %(total_number_of_records)s </b>subjects"), {'total_number_of_records': total_number_of_records }, true);
            var select_all_link = "<a id='select_all_link' class=''> " + select_all_text + "</a>"
            var select_across_pages_message = interpolate(gettext("All %(number_of_records)s Subjects on this page are selected."), {'number_of_records': no_of_records_on_page}, true) + select_all_link;
            $("#subjects_table").before("<div id='select_all_message'>" + select_across_pages_message + "</div>");

            $('#select_all_link').click(function () {
                $('#select_all_link').addClass('selected');
            });
        }
    };
};

DW.ActionsMenu = function () {
    var action_buttons = $("#subjects_table_wrapper").find("button.action");
    for (var i = 0; i < action_buttons.length; i++) {
        $(action_buttons[i]).on("click", function (eventObject) {
            var number_of_selected_subjects = $(".styled_table tbody input:checkbox:checked").length;
            var section_to_show = number_of_selected_subjects ? "#action" : "#none-selected";
            $(this).dropdown("detach");
            $(this).dropdown("attach", section_to_show);
            var edit_option = $("a.edit");
            if (number_of_selected_subjects > 1) {
                edit_option.parent().addClass("disabled");
                edit_option.attr("disabled", "disabled").attr("title", gettext("Select 1 Data Sender only"));
            } else {
                edit_option.parent().removeClass("disabled");
                edit_option.removeAttr("title").removeAttr("disabled");
            }
        });
    }

    selected_ids = function () {
        return $.map($(".styled_table tbody input:checkbox:checked"), function (el, i) {
            return $(el).val()
        });
    };

    $("a.edit").live('click', function (eventObject) {
        if ($(this).parent().hasClass("disabled")) {
            e.preventDefault();
            return;
        }
        location.href = '/entity/subject/edit/' + subject_type.toLowerCase() + '/' + selected_ids()[0] + '/';
    });

    $("a.delete").live('click', function (eventObject) {
//        subject_type is defined in all_subjects.html and
        warnThenDeleteDialogBox(selected_ids(), subject_type.toLowerCase(), this);
    });
};

DW.SubjectSelectAllCheckbox = function (drawTable) {

    var subject_select_all = new DW.SubjectPagination(drawTable);

    var check_all_element = $(".styled_table thead input:checkbox");

    check_all_element.live('click', function (eventObject) {
        $(".styled_table tbody input:checkbox").attr("checked", eventObject.currentTarget.checked);
    });

    check_all_element.live('change', function (eventObject) {
        if (eventObject.currentTarget.checked) {
            var no_of_records_on_page = drawTable.fnGetData().length;
            var total_number_of_records = drawTable.fnSettings().fnRecordsDisplay();
            if (no_of_records_on_page != total_number_of_records) {
                subject_select_all.display_select_across_pages_message(no_of_records_on_page, total_number_of_records);
            }
        }
        else {
            subject_select_all.deactivate_select_across_pages();
        }
    });

    $(".styled_table tbody input:checkbox").live('click', function (eventObject) {
        var all_selected = $(".styled_table tbody input:checkbox:checked").length == $(".styled_table tbody input:checkbox").length;
        $(".styled_table thead input:checkbox").attr("checked", all_selected)
    });

    this.un_check = function () {
        check_all_element.attr("checked", false)
    }
};
