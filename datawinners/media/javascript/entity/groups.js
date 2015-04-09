DW.GroupManager = function(options){

    var all_groups_list = $('#all_groups');
    var cancel_dialog_link = $("#cancel_group_dialog");

    function disable_add_button() {
        var add_button = $('#add_contacts_to_group');
        if($('.add_or_remove').text() == "Add"){
            add_button.text(gettext('Adding...'));
        }
        else {
            add_button.text(gettext('Removing...'));
        }
        add_button.addClass('ui-state-disabled');
    }

    function enable_add_button() {
        var add_button = $('#add_contacts_to_group');
        add_button.text(gettext('Add'));
        add_button.removeClass('ui-state-disabled');
    }

    $("#add_contacts_to_group").on('click', function(){
        var group_names = [];
        $("#all_groups input:checked").each(function(index, item){
            group_names.push(item.value);
        });
        if (!group_names.length > 0) {
            $('#no_group_selected_message').removeClass('none');
            return;
        }
        else{
            $('#no_group_selected_message').addClass('none');
        }
        DW.loading();
        disable_add_button();
        var contacts = all_groups_list.data()['selected_ids'];
        var current_group_name = all_groups_list.data()['current_group_name'];
        var all_selected = all_groups_list.data()['all_selected'];
        var action = all_groups_list.data()['action'];
        $.ajax({
            url: options.update_groups_url,
            type: "POST",
            headers: { "X-CSRFToken": $.cookie('csrftoken') },
            'data': {
                'group-names': JSON.stringify(group_names),
                'contact_ids':JSON.stringify(contacts),
                'all_selected' : all_selected,
                'current_group_name': current_group_name,
                'action': action,
                'search_query': $(".dataTables_filter input").val()
        }}).done(function(response){
            enable_add_button();
            DW.flashMessage(response.message, response.success);
            $("#all_groups_block").dialog("close");
        });

    });

    cancel_dialog_link.on('click', function(){
        $("#all_groups_block").dialog("close");
    });

};
