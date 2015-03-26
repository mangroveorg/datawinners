 $(function(){
        function col(header_class_name){
            return $('#datasender_table th.' + header_class_name).index('#datasender_table th');
        }

        var action_handler = new DW.DataSenderActionHandler();

        function filter_as_json(){
            return {'group_name': selected_group}
        }
        $("#datasender_table").dwTable({
                "concept": "Contact",
                "sAjaxSource": datasender_ajax_url,
                "sAjaxDataIdColIndex" : col("short_code"),
                "bServerSide": true,
                "iDeferLoading": 0,
                "oLanguage": {
                    "sEmptyTable": $('#no_registered_subject_message').clone(true, true).html()
                },
                "aaSorting": [ [ col("name"), "asc"] ] ,
                "actionItems" : [
                    {"label":"Add to Questionnaire", handler:action_handler.associate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                    {"label":"Remove from Questionnaire", handler:action_handler.disassociate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                    {"label":"Send an SMS", handler:action_handler.sendAMessage, "allow_selection":"multiple"},
                    {"label":"Give Web Submission Access", handler:action_handler.makewebuser, "allow_selection": "multiple"},
                    {"label":"Add to Groups", handler:action_handler.addtogroups, "allow_selection": "multiple"},
                    {"label":"Edit", handler:action_handler.edit, "allow_selection": "single"},
                    {"label": "Delete", "handler":action_handler["delete"], "allow_selection": "multiple"}
                ],
                "aoColumnDefs":[
                                {"bSortable": false, "aTargets":[col("devices"),col("projects"), col("s-groups")]}
                               ],
                "getFilter": filter_as_json

          });
        initializeContactGroupViewModel();
        var groupPanel = $("#group_panel");
        ko.applyBindings(groupViewModel, groupPanel[0]);
        groupViewModel.changeSelectedGroup(groupViewModel.groups()[0]);
        DW.GroupManager({'assign_contact_to_groups_url': assign_contact_to_groups_url});
});
