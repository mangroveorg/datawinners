describe("Generic Actions Test", function () {

    var onSuccess, onFailure;
    var serviceUrl;
    var deleteSpyedHandler, editSpyedHandler;

    beforeEach(function () {
        setFixtures('<div id="table-wrapper"><table id="simpleTable" ><thead><tr></tr></thead></table></div>');

        onSuccess = jasmine.createSpy('onSuccess');
        onFailure = jasmine.createSpy('onFailure');
        serviceUrl = '/entity/subjects/clinic/ajax/';

        setupSpyForTableData();

        deleteSpyedHandler = jasmine.createSpy();
        editSpyedHandler = jasmine.createSpy();
        $("#simpleTable").dwTable({
            "concept": "Subject",
            "sAjaxSource": serviceUrl,
            "sAjaxDataIdColIndex": 6,
            "iDisplayLength": 10,
            "bServerSide": true, "actionItems": [
                {"label": "Delete", handler: deleteSpyedHandler, "allow_selection": "multiple"},
                {"label": "Edit", handler: editSpyedHandler, "allow_selection": "single"}
            ],
            "aoColumns": [
                { "sTitle": "Engine" },
                { "sTitle": "Browser" },
                { "sTitle": "Platform" },
                { "sTitle": "devices", "sClass": "center" },
                { "sTitle": "devices", "sClass": "center" },
                { "sTitle": "devices", "sClass": "center" }
            ]
        });
    });

    it('should find delete handler called', function () {
        var table_object = $("#simpleTable_wrapper");
        clickFirstRowCheckBox(table_object);
        clickActionButton(table_object);
        clickMenuItem(".delete");
        expect(deleteSpyedHandler).toHaveBeenCalled();
    });

    it('should find edit called if only one row selected', function () {
        var table_object = $("#simpleTable_wrapper");
        clickFirstRowCheckBox(table_object);
        clickActionButton(table_object);
        clickMenuItem(".edit");
        expect(editSpyedHandler).toHaveBeenCalled();
    });

    it('Edit should be disabled if more than one row selected', function () {
        var table_object = $("#simpleTable_wrapper");
        select_all_rows(table_object);
        clickActionButton(table_object);
        expect(menuItemDisabled('.edit')).toBe(true);
        clickActionButton(table_object);
    });

    function clickActionButton(table) {
        table.find('.table_action_button').first().find('button').click();
    }

    function clickMenuItem(menuItemClass) {
        getActionItem(menuItemClass).click();
    }

    function menuItemDisabled(menuItemClass) {
        var action_button = getActionItem(menuItemClass);
        return action_button.parent().attr('class').indexOf('disabled') != -1;
    }

    function getActionItem(menuItemClass) {
        var action_button;
        $("div[id*='dropdown-menu']").each(function () {
            if (($(this).attr('style')) != 'display:none;') {
                action_button = $(this).find(menuItemClass)
            }
        });
        return action_button;
    }

    function clickFirstRowCheckBox(table) {
        table.find('table tbody tr td input:first').click();
    }

    function select_all_rows(table_object) {
        var checkallBox = table_object.find('.checkall-checkbox');
        // click handler is called before the checked value is updated; so setting checked value explicitly
        checkallBox.prop('checked', true);
        checkallBox.click();
        // the above click makes the checked value false; manually setting to true
        checkallBox.prop('checked', true);
    }
});