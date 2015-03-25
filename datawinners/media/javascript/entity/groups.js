$(function(){

    $("#add_contacts_to_group").on('click', function(){
        var group_names = [];
        $("#all_groups input:checked").each(function(index, item){
            group_names.push(item.value);
        });

        var contacts = $('#all_groups').data()['selected_ids'];
        var current_group_name = $('#all_groups').data()['current_group_name'];
        var all_selected = $('#all_groups').data()['all_selected'];
        $.ajax({
            url: assign_contact_to_groups_url,
            type: "POST",
            headers: { "X-CSRFToken": $.cookie('csrftoken') },
            'data': {
                'group-names': JSON.stringify(group_names),
                'contact_ids':JSON.stringify(contacts),
                'all_selected' : all_selected,
                'current_group_name': current_group_name
        }}).done(function(response){
            console.log(response.success);
        });

    });

    $("#cancel_group_dialog").on('click', function(){
        $("#all_groups_block").dialog("close");
    });


});