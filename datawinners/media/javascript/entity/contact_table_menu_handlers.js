(function(dw, $){
    dw.allContactTableMenu = {};
    dw.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent = function(){
        var removeGroupMenuItem = $($('#remove-from-group').parent());
        if(groupViewModel.isCustomGroupsPresent()){
            removeGroupMenuItem.removeClass('disabled');
        }
        else{
            removeGroupMenuItem.addClass('disabled');
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
}(DW, jQuery));
