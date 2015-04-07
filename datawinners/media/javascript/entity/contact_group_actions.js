(function(dw, $){

function _populate_group_dialog(groupNames){
    var allGroupsSection = $("#all_groups");
    $.each(groupNames, function (index, group_name) {
        allGroupsSection.append($("<li><label><input type='checkbox' value='" + group_name + "'>" + group_name + "</label></li>"));
    });
}


function _post_populating_of_remove_group_list(selected_ids, all_selected){
    var allGroupsSection = $("#all_groups");
    allGroupsSection.data("selected_ids", selected_ids);
    allGroupsSection.data("all_selected", all_selected);
    allGroupsSection.data("action", 'remove');
    allGroupsSection.data("current_group_name", selected_group);

    init_dialog_box_for_group();
    $('#no_group_selected_message').addClass('none');

    $('.add_or_remove').text(gettext("Remove"));
    $('#all_groups_block').dialog("option", "title", gettext('Remove from Groups'));
    $('#all_groups_block').dialog("open");
}

dw.addContactToGroup = function (selected_ids, all_selected) {
    dw.loading();
    $.get(all_groups_url).done(function (response) {
            var allGroupsSection = $("#all_groups");
            allGroupsSection.html("");
            var groupNames = _.map(response.group_details, function(groupItem){ return groupItem.name;});
            _populate_group_dialog(groupNames);
            allGroupsSection.data("selected_ids", selected_ids);
            allGroupsSection.data("all_selected", all_selected);
            allGroupsSection.data("action", "add");
            allGroupsSection.data("current_group_name", selected_group);

            init_dialog_box_for_group();
            $('#no_group_selected_message').addClass('none');

            $('.add_or_remove').text(gettext("Add"));
            $('#all_groups_block').dialog("option", "title", gettext('Add to Groups'));
            $('#all_groups_block').dialog("open");
        }
    );
}

dw.removeFromGroup = function (selected_ids, all_selected) {
    if(all_selected){
            DW.loading();
            $.get(all_groups_url).done(function (response) {
                var allGroupsSection = $("#all_groups");
                allGroupsSection.html("");
                var groupNames = _.map(response.group_details, function(groupItem){ return groupItem.name;});
                _populate_group_dialog(groupNames);
                _post_populating_of_remove_group_list(selected_ids, all_selected);
            }
        );
    }
    else{
        var all_selected_groups = []
         $.each(selected_ids, function(index, rep_id){
            var children = $("input[value=" + rep_id + "]").closest("tr").children();
            var group_names = $(children[9]).text().split(", ");
             $.each(group_names, function(index, group_name){
                 if(group_name != ""){
                     all_selected_groups.push(group_name);
                 }
             });
         });
        var sorted_unique_group_names = _.sortBy(_.union(all_selected_groups), function(group_name){return group_name.toLowerCase(); });
        var allGroupsSection = $("#all_groups");
        allGroupsSection.html("");
        var prioritized_list = _.reject(sorted_unique_group_names, function(item){ return item == selected_group; });
        if(prioritized_list.length + 1 == sorted_unique_group_names.length){
            prioritized_list.unshift(selected_group);
        }
        _populate_group_dialog(prioritized_list);
        _post_populating_of_remove_group_list(selected_ids, all_selected);
    }
}

}(DW, jQuery));

