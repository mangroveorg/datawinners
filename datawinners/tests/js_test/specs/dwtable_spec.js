describe("dwtable test", function () {
    var table;
    var getPaginationButton = function (pagination_link) {
        var pagination_button = null;
        $("div[id*='pagination_more_menu']").each(function () {
            if (($(this).attr('style')) != 'display:none;') {
                pagination_button = $(this).find($("a[id*='" + pagination_link + "']"));
            }
        });

        return pagination_button;

    }

    beforeEach(function () {
        setFixtures('<div id="table-wrapper"><table id="simpleTable" ><thead><tr></tr></thead></table></div>');
        setupSpyForTableData();


        $("#simpleTable").dwTable({
            "concept": "Subject",
            "sAjaxSource": '/entity/subjects/clinic/ajax/',
            "sAjaxDataIdColIndex": 6,
            "iDisplayLength": 10,
            "bServerSide": true, "actionItems": [
                {"label": "Delete", handler: function (tb) {
                    alert('delete' + tb);
                }, "allow_selection": "multiple"},
                {"label": "Edit", handler: function () {
                    alert('edit');
                }, "allow_selection": "single"}
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
        table = $("#simpleTable_wrapper");

    });

    it('should find Select a Subject as menu item when no row is selected', function () {
        $($.find('button')[0]).trigger('click');
        expect($('.dropdown ul li.none-selected').text()).toEqual('Select a Subject');
        $($.find('button')[0]).trigger('click')
    });

    it('should find Select all link when all rows in the page are selected', function () {
        select_all_rows(table, true);
        expect(table.find('.table_wrapper .select_all_message').text()).toEqual("You have selected 10 Subject(s) on this page. Select all  30 Subject(s)")
    });

    it('should find Clear all link when Select all is clicked and should disappear when Clear Selection is clicked', function () {
        select_all_rows(table, true);
        table.find('.select_all_message a').click();
        expect(table.find('.select_all_message').text()).toEqual('You have selected all 30 Subject(s). Clear Selection');

        table.find('.select_all_message a').click();
        expect(table.find('tbody tr:first')).toBeHidden();
    });

    it('clear check-all and select all>all div when any of checkbox is unchecked', function () {
        select_all_rows(table, true);
        table.find('.select_all_message a').click();
        expect(table.find('.select_all_message').text()).toEqual('You have selected all 30 Subject(s). Clear Selection');
        check_a_checkbox(table.find('.row_checkbox:first'),false);
        expect(table.find('tbody tr:first')).toBeHidden();
        expect(table.find('.checkall-checkbox')).not.toBeChecked();
    });

    it('should not find Select all>all when number of rows are less than page size', function () {
        var pagesize = 50;
        change_page_size_to(pagesize);
        select_all_rows(table, true);
        expect(table.find('tbody tr:first')).toBeHidden();
    });

    it('should verify number of table rows and pagination text when page size is changed', function () {
        verifyInitialState(table);

        var pagesize = 50;
        change_page_size_to(pagesize);
        expect(table.find('.row_checkbox')).toHaveLength(30);
        expect(table.find('.dataTables_info').first()).toHaveText('1 to 30 of 30 Subject(s)');

    });


    it('should reset to first page when page size is changed from a different page', function () {
        table.find('.paginate_enabled_next:first').click();
        expect(table.find('.dataTables_info').first()).toHaveText('11 to 20 of 30 Subject(s)');
        change_page_size_to(25);
        expect(table.find('.dataTables_info').first()).toHaveText('1 to 25 of 30 Subject(s)');

    });

    it('should find the Search text in the ajax call', function () {
        var searchText = "someSearchText";
        var table = $("#simpleTable_wrapper");
        table.find('.dataTables_filter input').val(searchText).trigger('keyup');
        var params = $.ajax.mostRecentCall.args[0];
        var searchTerm = ajaxRequestDataValue(params.data, 'sSearch');
        expect(searchTerm).toEqual(searchText);
    });


    it('should go to next page when paginate-next button is clicked', function () {
        var previous_page_button = table.find('.paginate_disabled_previous:first');
        expect(previous_page_button).not.toBeNull();
        table.find('.paginate_enabled_next:first').click();
        expect(table.find('.dataTables_info').first()).toHaveText('11 to 20 of 30 Subject(s)');
    });

    it('should check visibility of pagination first and last buttons', function () {
        table.find('.paginate_more:first').click();

        expect(getPaginationButton("first_page").parent()).toHaveAttr('class', 'disabled');

        getPaginationButton("last_page").click();
        expect(table.find('.dataTables_info').first()).toHaveText('21 to 30 of 30 Subject(s)');

        table.find('.paginate_more:first').click();
        expect(getPaginationButton("last_page").parent()).toHaveAttr('class', 'disabled');
        expect(getPaginationButton("first_page").parent()).not.toHaveAttr('class', 'disabled');
        table.find('.paginate_more:first').click();
    });


    it('All the pagination button should be enabled when in records exist in previous and next pages', function () {
        table.find('.paginate_enabled_next:first').click();
        expect(table.find('.dataTables_info').first()).toHaveText('11 to 20 of 30 Subject(s)');
        expect(table.find('.paginate_enabled_next:first')).not.toBeNull();
        expect(table.find('.paginate_enabled_previous:first')).not.toBeNull();
        table.find('.paginate_more:first').click();
        expect(getPaginationButton("first_page").parent()).not.toHaveAttr('class', 'disabled');
        expect(getPaginationButton("last_page").parent()).not.toHaveAttr('class', 'disabled');
        table.find('.paginate_more:first').click();
    });

    it('should clear select all master checkbox when one checkbox is unselected', function () {
        select_all_rows(table, true);
        check_a_checkbox(table.find('.row_checkbox:first'),false);
        expect(table.find('.checkall-checkbox')).not.toBeChecked();
        check_a_checkbox(table.find('.row_checkbox:first'),true);
        expect(table.find('.checkall-checkbox')).toBeChecked();
    });

    it('should select master checkbox when all rows in the table are selected',function(){
        var master_checkbox = table.find('.checkall-checkbox');
        table.find('.row_checkbox').each(function(){
            check_a_checkbox($(this),true);
        });
        expect(master_checkbox).toBeChecked();
    });
    function verifyInitialState(table) {
        expect(table.find('.dataTables_info').first()).toHaveText('1 to 10 of 30 Subject(s)');
        expect(table.find('.row_checkbox')).toHaveLength(10);
    }


    function select_all_rows(table, check) {
        check_a_checkbox(table.find('.checkall-checkbox'),check)
    }

    function check_a_checkbox(checkbox, check) {
        // click handler is called before the checked value is updated; so setting checked value explicitly
        checkbox.prop('checked', check);
        checkbox.click();
        // the above click makes the checked value false; manually setting to true
        checkbox.prop('checked', check);
    }

    function change_page_size_to(page_size) {
        $('#simpleTable_length select').val(page_size).change()
    }

});
