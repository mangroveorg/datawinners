 $(function(){
        function col(header_class_name){
            return $('#datasender_table th.' + header_class_name).index('#datasender_table th');
        }

        var action_handler = new DW.DataSenderActionHandler();


        $("#datasender_table").dwTable({
                "concept": "Contact",
                "sAjaxSource": datasender_ajax_url,
                "sAjaxDataIdColIndex" : col("short_code"),
                "bServerSide": true,
                "oLanguage": {
                    "sEmptyTable": $('#no_registered_subject_message').clone(true, true).html()
                },
                "aaSorting": [ [ col("name"), "asc"] ] ,
                "actionItems" : [
                    {"label":"Add to Questionnaire", handler:action_handler.associate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                    {"label":"Remove from Questionnaire", handler:action_handler.disassociate, "allow_selection": number_of_projects==0?"disabled":"multiple"},
                    {"label":"Send an SMS", handler:action_handler.sendAMessage, "allow_selection":"multiple"},
                    {"label":"Give Web Submission Access", handler:action_handler.makewebuser, "allow_selection": "multiple"},
                    {"label":"Edit", handler:action_handler.edit, "allow_selection": "single"},
                    {"label": "Delete", "handler":action_handler["delete"], "allow_selection": "multiple"}
                ],
                "aoColumnDefs":[
                                {"bSortable": false, "aTargets":[col("devices"),col("projects"), col("s-groups")]}
                               ]

          });
});
