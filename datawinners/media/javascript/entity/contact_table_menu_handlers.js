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

        if(isContactsAcrossPagesSelected && groupViewModel.isCustomGroupsPresent()){
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

        if(dw.allContactTableMenu.canRemoveQuestionnaire(selectedContacts)){
            removeQuestionnaireMenuItem.removeClass('disabled');
        }
        else{
            removeQuestionnaireMenuItem.addClass('disabled');
        }
    };

    $(document).ready(function() {
        $.each($("input[name='project_names']"), function(index, element) {
           project_list.push(element.value);
        });
    });

    dw.allContactTableMenu.canRemoveQuestionnaire = function(selectedContacts){
        var selectedIds = _.map(selectedContacts, function(elem){ return elem.value})
        var currentQuestionnaireList = dw.matchingQuestionnaireNames(selectedIds);
        var commonQuestionnaires = _.intersection(project_list, currentQuestionnaireList);
        return commonQuestionnaires.length > 0;
    }

    dw.allContactTableMenu.disableMenuItemWhenAccountIsNotProSMS = function(){
        var sendSmsMenuItem = $($('#send-an-sms').parent());
        if(is_pro_sms == 'False'){
            sendSmsMenuItem.remove();
        }
    }
}(DW, jQuery));
