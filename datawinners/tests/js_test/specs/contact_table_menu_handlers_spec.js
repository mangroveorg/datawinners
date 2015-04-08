describe('contact table menu items', function () {

    var $removeFromGroupParent;

    beforeEach(function(){
        $removeFromGroupParent = $('#remove-from-group-parent');
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

        xit("should disable group when selected contacts does not belong to any group", function (){

            $removeFromGroupParent.removeClass('disabled');

            DW.allContactTableMenu.disableMenuItemWhenSelectedContactsHaveNoGroup();

            expect($removeFromGroupParent).toHaveClass('disabled');

        });
    });



});
