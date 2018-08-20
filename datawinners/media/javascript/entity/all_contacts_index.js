 $(function(){
    function col(header_class_name){
        return $('#datasender_table th.' + header_class_name).index('#datasender_table th');
    }

    var action_handler = new DW.DataSenderActionHandler();

    function filter_as_json(){
        return {'group_name': selected_group}
    }

    initializeContactGroupViewModel();

    $("#datasender_table").dwTable({
            "concept": "Contact",
            "sAjaxSource": datasender_ajax_url,
            "sAjaxDataIdColIndex" : col("short_code"),
            "bServerSide": true,
            "onMenuLoad":function(){
                DW.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent();
                DW.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup();
                DW.allContactTableMenu.disableMenuItemWhenSelectedContactHaveNoQuestionnaire();
                DW.allContactTableMenu.disableMenuItemWhenAccountIsNotProSMS();
            },
            "iDeferLoading": 0,
            "oLanguage": {
                "sEmptyTable": $('#no_datasenders_message').clone(true, true).html()
            },
            "aaSorting": [ [ col("name"), "asc"] ] ,
            "actionItems" : [
                {"label":"Send an SMS", "id":"send-an-sms",handler:action_handler.sendAMessage, "allow_selection":"multiple"},
                {"label":"Add to Questionnaires", handler:action_handler.associate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                {"label":"Remove from Questionnaires", "id":"remove-from-questionnaire", handler:action_handler.disassociate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                {"label":"Add to Groups", "id": "add-to-group", handler:action_handler.addtogroups, "allow_selection":"multiple"},
                {"label":"Add to new Group", "id":"add-to-new-group", handler: action_handler.addToNewGroup, "allow_selection": "multiple"},
                {"label":"Remove from Groups", "id": "remove-from-group", handler:action_handler.removefromgroups, "allow_selection":"multiple"},
                {"label":"Edit", handler:action_handler.edit, "allow_selection": "single"},
                {"label":"Add E-mail address", "id": "add-email", handler:action_handler.makewebuser, "allow_selection": "multiple"},
                {"label": "Delete", "handler":action_handler["delete"], "allow_selection": "multiple"}
            ],
            "aoColumnDefs":[
                            {"bSortable": false, "aTargets":[col("devices"),col("projects"), col("s-groups"), col('groups')]}
                           ],
            "getFilter": filter_as_json

      });
    groupViewModel.changeSelectedGroup(groupViewModel.groups()[0]);
    DW.GroupManager({'update_groups_url': update_groups_url});

    var groupDeleteDialog = $("#group-delete-confirmation-section");
    groupDeleteDialog.dialog({
        autoOpen: false,
        modal: true,
        title: gettext("Warning!"),
        zIndex: 700,
        width: 500,
        height: 'auto'
    });

     var groupRenameDialog = $('#group-rename-confirmation-section');
     groupRenameDialog.dialog({
         autoOpen: false,
         modal: true,
         title: gettext("Rename Group"),
         zIndex: 700,
         width: 470,
         height: 'auto',
         close: function(){ $("#new_group_mandatory_error").addClass("none");}
     });

});
