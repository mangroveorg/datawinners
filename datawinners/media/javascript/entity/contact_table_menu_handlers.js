(function(dw, $){
    dw.allContactTableMenu = {};
    dw.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent = function(){
        var removeGroupMenuItem = $($('#remove-from-group').parent());
        var addGroupMenuItem = $($('#add-to-group').parent());
        if(groupViewModel.isCustomGroupsPresent()){
            removeGroupMenuItem.removeClass('disabled');
            addGroupMenuItem.removeClass('disabled');
        }
        else{
            removeGroupMenuItem.addClass('disabled');
            addGroupMenuItem.addClass('disabled');
        }
    };

    dw.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup = function(){

        var $datasenderTable = $("#datasender_table");
        var selectedContacts = $datasenderTable.find("input.row_checkbox:checked");
        var isContactsAcrossPagesSelected = $datasenderTable.find(".select_all_message").data('all_selected');
        var removeGroupMenuItem = $($('#remove-from-group').parent());

        if(isContactsAcrossPagesSelected){
            removeGroupMenuItem.removeClass('disabled');
            return;
        }

        var contactRowWithGroup = _.find(selectedContacts, function(item){
                return $($(item).closest("tr").children()[9]).text() != "";
        });

        if(contactRowWithGroup){
            removeGroupMenuItem.removeClass('disabled');
        }
        else{
            removeGroupMenuItem.addClass('disabled');
        }
    };

    dw.allContactTableMenu.disableMenuItemWhenSelectedContactHaveNoQuestionnaire = function(){
        var $datasenderTable = $("#datasender_table");
        var selectedContacts = $datasenderTable.find("input.row_checkbox:checked");
        var isContactsAcrossPagesSelected = $datasenderTable.find(".select_all_message").data('all_selected');
        var removeQuestionnaireMenuItem = $($('#remove-from-questionnaire').parent());


        if(isContactsAcrossPagesSelected){
            removeQuestionnaireMenuItem.removeClass('disabled');
            return;
        }

        var contactRowWithQuestionnaire = _.find(selectedContacts, function(item){
                return $($(item).closest("tr").children()[7]).text() != "";
        });

        if(contactRowWithQuestionnaire){
            removeQuestionnaireMenuItem.removeClass('disabled');
        }
        else{
            removeQuestionnaireMenuItem.addClass('disabled');
        }
    }
}(DW, jQuery));
