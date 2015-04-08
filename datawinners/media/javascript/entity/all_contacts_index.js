 $(function(){
    function col(header_class_name){
        return $('#datasender_table th.' + header_class_name).index('#datasender_table th');
    }

    var action_handler = new DW.DataSenderActionHandler();

    function filter_as_json(){
        return {'group_name': selected_group}
    }

    initializeContactGroupViewModel();

    var _disableGroupMenuItemsWhenNoGroupsPresent = function(){
        var removeGroupMenuItem = $($('#remove-from-group').parent());
        if(groupViewModel.isCustomGroupsPresent()){
            removeGroupMenuItem.removeClass('disabled');
        }
        else{
            removeGroupMenuItem.addClass('disabled');
        }
    };

    var _disableMenuItemWhenSelectedContactsHaveNoGroup = function(){
        var selectedContacts = $("#datasender_table").find("input.row_checkbox:checked");
        var contactRowWithGroup = _.find(selectedContacts, function(item){
                return $($(item).closest("tr").children()[9]).text() != "";
            });
        var removeGroupMenuItem = $($('#remove-from-group').parent());
        if(contactRowWithGroup){
            removeGroupMenuItem.removeClass('disabled');
        }
        else{
            removeGroupMenuItem.addClass('disabled');
        }
    };

    $("#datasender_table").dwTable({
            "concept": "Contact",
            "sAjaxSource": datasender_ajax_url,
            "sAjaxDataIdColIndex" : col("short_code"),
            "bServerSide": true,
            "onMenuLoad":function(){
                DW.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent();
                DW.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup();
            },
            "iDeferLoading": 0,
            "oLanguage": {
                "sEmptyTable": $('#no_datasenders_message').clone(true, true).html()
            },
            "aaSorting": [ [ col("name"), "asc"] ] ,
            "actionItems" : [
                {"label":"Add to Questionnaire", handler:action_handler.associate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                {"label":"Remove from Questionnaire", handler:action_handler.disassociate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                {"label":"Send an SMS", handler:action_handler.sendAMessage, "allow_selection":"multiple"},
                {"label":"Give Web Submission Access", handler:action_handler.makewebuser, "allow_selection": "multiple"},
                {"label":"Add to Groups", handler:action_handler.addtogroups, "allow_selection":"multiple"},
                {"label":"Remove from Groups", "id": "remove-from-group", handler:action_handler.removefromgroups, "allow_selection":"multiple"},
                {"label":"Edit", handler:action_handler.edit, "allow_selection": "single"},
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
