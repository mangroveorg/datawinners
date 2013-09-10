DW = DW || {};

DW.DeleteAction = function (delete_block_selector, delete_end_point) {
    var delete_entity_block = $(delete_block_selector);

    delete_entity_block.dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: false,
            width: 500,
            closeText: 'hide'
        }
    );

    $(".cancel_link", delete_block_selector).on("click", function () {
        delete_entity_block.dialog("close");
        return false;
    });


    $("#ok_button", delete_block_selector).on("click", function () {
        delete_entity_block.dialog("close");
        var allIds = delete_entity_block.data("allIds");
        var post_data = {'all_ids': allIds.join(';'), 'entity_type': delete_entity_block.data("entity_type")};
        var project_name = $("#project_name");
        if (project_name.length)
            post_data.project = project_name.val();
        post_data.all_selected = $("#select_all_message").data("all_selected");
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
        $.post(delete_end_point, post_data,
            function (json_response) {
                var response = $.parseJSON(json_response);
                $.unblockUI();
                if (response.success) {
                    window.location.reload();
                }
            }
        );
        return false;
    });


    this.open = function (selected_ids, entity_type) {
        delete_entity_block.data("allIds", selected_ids);
        delete_entity_block.data("entity_type", entity_type);
        delete_entity_block.dialog("open");
    }
};

DW.ActionsMenu = function () {
    var delete_action = new DW.DeleteAction("#delete_entity_block", "/entity/subjects/delete/");
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

    function selected_ids() {
        return $.map($(".styled_table tbody input:checkbox:checked"), function (el) {
            return $(el).val();
        });
    }

    $("a.edit").live('click', function (eventObject) {
        if ($(this).parent().hasClass("disabled")) {
            e.preventDefault();
            return;
        }
        location.href = edit_url_template.replace("entity_id_placeholder", selected_ids()[0]);
    });

    $("a.delete").live('click', function (eventObject) {
        delete_action.open(selected_ids(), subject_type.toLowerCase());
    });
};


DW.SubjectPagination = function () {
    $("#subjects_table").before("<div id='select_all_message'></div>");
    var select_all_message = $("#select_all_message");

    this.disable = function () {
        select_all_message.html('');
        select_all_message.removeData("all_selected");
    };

    this.enable = function (no_of_records_on_page, total_number_of_records) {
        var select_all_text = interpolate(gettext("Select all <b> %(total_number_of_records)s </b>subjects"),
            {'total_number_of_records': total_number_of_records }, true);
        var select_all_link = "<a id='select_all_link' class=''> " + select_all_text + "</a>";
        var select_across_pages_message = interpolate(gettext("All %(number_of_records)s Subjects on this page are selected."),
            {'number_of_records': no_of_records_on_page}, true) + select_all_link;
        select_all_message.html(select_across_pages_message);

        $('#select_all_link').click(function () {
            select_all_message.html(interpolate(gettext("All %(total_number_of_records)s Subjects selected."),
                {'total_number_of_records': total_number_of_records }, true));
            select_all_message.data('all_selected', true);
        });
    };
};


DW.SubjectSelectAllCheckbox = function (drawTable) {
    var subject_select_all = new DW.SubjectPagination();
    var check_all_element = $(".styled_table thead input:checkbox");

    check_all_element.live('click', function (eventObject) {
        $(".styled_table tbody input:checkbox").attr("checked", eventObject.currentTarget.checked);
    });

    check_all_element.live('change', function (eventObject) {
        if (eventObject.currentTarget.checked) {
            var no_of_records_on_page = drawTable.fnGetData().length;
            var total_number_of_records = drawTable.fnSettings().fnRecordsDisplay();
            if (no_of_records_on_page != total_number_of_records) {
                subject_select_all.enable(no_of_records_on_page, total_number_of_records);
            }
        }
        else {
            subject_select_all.disable();
        }
    });

    $(".styled_table tbody input:checkbox").live('click', function (eventObject) {
        var all_selected = $(".styled_table tbody input:checkbox:checked").length == $(".styled_table tbody input:checkbox").length;
        $(".styled_table thead input:checkbox").attr("checked", all_selected)
    });

    this.un_check = function () {
        check_all_element.attr("checked", false);
        subject_select_all.disable();
    }
};
