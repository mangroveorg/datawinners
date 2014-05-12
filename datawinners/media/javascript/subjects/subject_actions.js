DW = DW || {};

DW.DeleteAction = function (delete_block_selector, delete_end_point) {
    var delete_entity_block = $(delete_block_selector);

    delete_entity_block.dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: false,
            width: 520,
            closeText: 'hide'
        }
    );

    $(".cancel_link", delete_block_selector).click(function () {
        delete_entity_block.dialog("close");
        return false;
    });


    $("#ok_button", delete_block_selector).click(function () {
        delete_entity_block.dialog("close");
        var allIds = delete_entity_block.data("allIds");
        var post_data = {'all_ids': allIds.join(';'), 'entity_type': delete_entity_block.data("entity_type")};
        var project_name = $("#project_name");
        if (project_name.length)
            post_data.project = project_name.val();
        post_data.all_selected = delete_entity_block.data("all_selected");
        post_data.search_query = $("#subjects_table_filter").find("input").val();
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


    this.open = function (entity_type, selected_ids, all_selected) {
        delete_entity_block.data("allIds", selected_ids);
        delete_entity_block.data("all_selected", all_selected);
        delete_entity_block.data("entity_type", entity_type);
        delete_entity_block.dialog("open");
    }
};

DW.AllSubjectActions = function () {
    this["delete"] = function(table, selected_ids, all_selected){
        var delete_action = new DW.DeleteAction("#delete_entity_block", "/entity/subjects/delete/");
        delete_action.open(subject_type.toLowerCase(), selected_ids, all_selected);
    }

    this["edit"] = function(table, selected_ids){
        window.location.href = edit_url_template.replace("entity_id_placeholder", selected_ids[0]);
    }
};



