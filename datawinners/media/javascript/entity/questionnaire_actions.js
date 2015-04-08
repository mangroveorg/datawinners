(function(dw, $) {


        dw.addToQuestionnaire =   function (table, selected_ids, all_selected) {
        var all_project_block = $("#all_project_block");
        all_project_block.find('#error').remove();
        $('#all_project_block :checked').attr("checked", false);

        $.each($("#all_projects li"), function (index, item) {
            $(item).show();
        });

        all_project_block.data("selected_ids", selected_ids);
        all_project_block.data("all_selected", all_selected);
        all_project_block.data("action", "associate");
        all_project_block.data("pageToGo", get_updated_table_page_index(table, selected_ids, all_selected));

        $('#action_for_project').text(gettext("Add"));
        all_project_block.dialog('option', 'title', gettext('Add to Questionnaire'));
        all_project_block.dialog("open");
    }

    function _matchingQuestionnaireNames(selectedIds) {
        var all_matching_questionnaires = [];
        $.each(selectedIds, function (index, rep_id) {
            var children = $("input[value=" + rep_id + "]").closest("tr").children();
            var questionnaire_names = $(children[7]).text().split(", ");
            $.each(questionnaire_names, function (index, questionnaire_name) {
                if (questionnaire_name != "") {
                    all_matching_questionnaires.push(questionnaire_name);
                }
            });
        });
        var unique_questionnaire_names = _.union(all_matching_questionnaires);
        return unique_questionnaire_names;
    }

    dw.removeFromQuestionnaire = function (table, selected_ids, all_selected) {
        var all_project_block = $("#all_project_block");
        all_project_block.find('#error').remove();
        $('#all_project_block :checked').attr("checked", false);

        if (!all_selected) {
            var unique_questionnaire_names = _matchingQuestionnaireNames(selected_ids)
            $.each($("#all_projects li"), function (index, item) {
                var $item = $(item);
                if (unique_questionnaire_names.indexOf($item.text()) > -1) {
                    $item.show();
                }
                else {
                    $item.hide();
                }
            });
        }

        all_project_block.data("selected_ids", selected_ids);
        all_project_block.data("all_selected", all_selected);
        all_project_block.data("action", "disassociate");
        all_project_block.data("pageToGo", get_updated_table_page_index(table, selected_ids, all_selected));

        $('#action_for_project').text(gettext("Remove"));
        all_project_block.dialog('option', 'title', gettext('Remove from Questionnaire'));
        all_project_block.dialog("open");
    }

}(DW, jQuery));