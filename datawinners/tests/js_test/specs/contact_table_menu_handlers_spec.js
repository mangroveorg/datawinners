describe('contact table menu items', function () {

    var $removeFromGroupParent;
    var $addToGroupParent;

    beforeEach(function(){
        $removeFromGroupParent = $('#remove-from-group-parent');
        $addToGroupParent = $('#add-to-group');
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

    });

});
