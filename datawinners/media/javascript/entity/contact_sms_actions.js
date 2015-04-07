(function(dw, $, ko, all_contacts_mobile_number_url){

    dw.populateAndShowSmsDialog = function (selected_ids, all_selected){
        if(all_selected){

            $.ajax({
                url: all_contacts_mobile_number_url,
                type: "POST",
                headers: { "X-CSRFToken": $.cookie('csrftoken') },
                data: {
                    'group_name':selected_group,
                    'search_query':$(".dataTables_filter input").val()
                }

            }).done(function (json_response) {
                var response =  $.parseJSON(json_response);
                _showSmsDialog(response['mobile_numbers'], response["contact_display_list"]);
            });

        }
        else{
            var contact_mobile_numbers = [];
            var contact_display_list = [];
            $.each(selected_ids, function(index, rep_id){
                var children = $("input[value=" + rep_id + "]").closest("tr").children();
                var mobile_number = $(children[2]).text();
                var contact_name = $(children[1]).text();
                var display_text = contact_name == "" ? mobile_number : contact_name
                contact_display_list.push(display_text + " ("+ rep_id +")");
                contact_mobile_numbers.push(mobile_number);
            });
            _showSmsDialog(contact_mobile_numbers.join(", "), contact_display_list.join(", "));
        }
    }

    function _showSmsDialog(contact_mobile_numbers, contact_display_list){
        var smsViewModel = ko.contextFor($("#send-sms-section")[0]).$root;
        smsViewModel.showToSection(false);
        smsViewModel.hideSpecifiedContacts(false);
        smsViewModel.selectedSmsOption("others");
        smsViewModel.othersList(contact_mobile_numbers);
        smsViewModel.specifiedList(contact_display_list);
        $("#send-sms-section").dialog('open');
    }

}(DW, jQuery, ko, all_contacts_mobile_number_url));