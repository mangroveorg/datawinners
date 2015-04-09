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

    dw.allContactTableMenu.disableMenuItemWhenSelectedContactHaveNoQuestionnaire = function(){
        var selectedContacts = $("#datasender_table").find("input.row_checkbox:checked");
        var contactRowWithQuestionnaire = _.find(selectedContacts, function(item){
                return $($(item).closest("tr").children()[7]).text() != "";
        });
        var removeQuestionnaireMenuItem = $($('#remove-from-questionnaire').parent());

        if(contactRowWithQuestionnaire){
            removeQuestionnaireMenuItem.removeClass('disabled');
        }
        else{
            removeQuestionnaireMenuItem.addClass('disabled');
        }
    }
}(DW, jQuery));
