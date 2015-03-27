DW.GroupManager = function(options){

    var all_groups_list = $('#all_groups');
    var cancel_dialog_link = $("#cancel_group_dialog");

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
        var contacts = all_groups_list.data()['selected_ids'];
        var current_group_name = all_groups_list.data()['current_group_name'];
        var all_selected = all_groups_list.data()['all_selected'];
        $.ajax({
            url: options.assign_contact_to_groups_url,
            type: "POST",
            headers: { "X-CSRFToken": $.cookie('csrftoken') },
            'data': {
                'group-names': JSON.stringify(group_names),
                'contact_ids':JSON.stringify(contacts),
                'all_selected' : all_selected,
                'current_group_name': current_group_name
        }}).done(function(response){
            flash_message(response.message, response.success);
            $("#datasender_table").dataTable().fnReloadAjax();
            $("#all_groups_block").dialog("close");
        });

    });

    cancel_dialog_link.on('click', function(){
        $("#all_groups_block").dialog("close");
    });

};
