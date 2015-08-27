describe('contact table menu items', function () {

    var $removeFromGroupParent;
    var $addToGroupParent;
    var $removeFromQuestionnaireParent;

    beforeEach(function(){
        $removeFromGroupParent = $('#remove-from-group-parent');
        $addToGroupParent = $('#add-to-group-parent');
        $removeFromQuestionnaireParent = $('#remove-from-questionnaire-parent');
        $('input:checkbox').removeAttr('checked');
    });

    describe("remove from group", function() {

        it("should disable when no groups present", function () {
            spyOn(groupViewModel, "isCustomGroupsPresent").andReturn(false);
            $removeFromGroupParent.removeClass('disabled');

            DW.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent();

            expect($removeFromGroupParent).toHaveClass('disabled');
        });

        it("should enable when groups are present", function () {
            spyOn(groupViewModel, "isCustomGroupsPresent").andReturn(true);
            $removeFromGroupParent.addClass('disabled');

            DW.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent();

            expect($removeFromGroupParent).not.toHaveClass('disabled');
        });

        it("should disable group when selected contacts does not belong to any group", function (){
            $removeFromGroupParent.removeClass('disabled');
            $("#id").click();

            DW.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup();

            expect($removeFromGroupParent).toHaveClass('disabled');
        });

         it("should not disable group when selected contacts belong to a group", function (){
            $removeFromGroupParent.addClass('disabled');
            $("#id4").click();

            DW.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup();

            expect($removeFromGroupParent).not.toHaveClass('disabled');

        });

        it("should enable menu item when select all all selected and custom group present", function (){
            $removeFromGroupParent.addClass('disabled');
            $("#all_selected_element").data('all_selected', true);
            spyOn(groupViewModel, "isCustomGroupsPresent").andReturn(true);

            DW.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup();

            expect($removeFromGroupParent).not.toHaveClass('disabled');

        });

        it("should disable menu item when select all all selected and no custom groups present", function (){
            $removeFromGroupParent.removeClass('disabled');
            $("#all_selected_element").data('all_selected', true);
            spyOn(groupViewModel, "isCustomGroupsPresent").andReturn(false);

            DW.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup();

            expect($removeFromGroupParent).toHaveClass('disabled');

        });


    });

    describe("add to group", function() {

        it('should disable when no group present', function(){
            spyOn(groupViewModel, "isCustomGroupsPresent").andReturn(false);
            $addToGroupParent.addClass('disabled');

            DW.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent();

            expect($addToGroupParent).toHaveClass('disabled');


        });

        it('should not disable when group present', function(){
            spyOn(groupViewModel, "isCustomGroupsPresent").andReturn(true);
            $addToGroupParent.addClass('disabled');

            DW.allContactTableMenu.disableGroupMenuItemsWhenNoGroupsPresent();

            expect($addToGroupParent).not.toHaveClass('disabled');

        });

    });

    describe("remove from questionnaire", function() {

        beforeEach(function() {
            $('input:checkbox').removeAttr('checked');
        });

        it('should be disabled when no contacts are not linked to questionnaires', function(){

            $removeFromQuestionnaireParent.removeClass('disabled');
            $("#all_selected_element").data('all_selected', false);
            $("#id5").click();

            DW.allContactTableMenu.disableMenuItemWhenSelectedContactHaveNoQuestionnaire();

            expect($removeFromQuestionnaireParent).toHaveClass('disabled');

        });

        it('should not be disabled when contacts are linked to questionnaires', function(){
            $removeFromQuestionnaireParent.addClass('disabled');

            $("#id6").click();

            DW.allContactTableMenu.disableMenuItemWhenSelectedContactHaveNoQuestionnaire();

            expect($removeFromQuestionnaireParent).not.toHaveClass('disabled');

        });

    });

});
