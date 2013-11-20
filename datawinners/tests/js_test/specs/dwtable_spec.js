describe("dwtable test", function () {

    var response_10_datarows = {responseText: {"iTotalRecords": 18, "data": [
        ["Clinic", "TSIMANARIRAZANA", "TSIMANARIRAZANA,ANDRAINJATO AVARATRA,FIANARANTSOA I,HAUTE MATSIATRA,Madagascar", "-12.35, 49.3", "87654325", "cli12"],
        ["Clinic", "Antalaha", "ANTALAHA,SAVA,Madagascar", "-14.8833, 50.25", "87654323", "cli10"],
        ["Clinic", "ANALAMANGA", "ANALAMANGA,Madagascar", "-18.8, 47.4833", "87654324", "cli11"],
        ["Kochi Clinic", "Test", "India,Kerala,Kochi", "9.939248, 76.259625", "123460", "cid005"],
        ["New Gwalior Clinic", "Test", "India,Madhya Pradesh,New Gwalior", "26.227112, 78.18708", "1234561", "cid006"],
        ["Indore Clinic", "Test", "India,Madhya Pradesh,Indore", "22.7167, 75.8", "1234562", "cid007"],
        ["Khandwa Clinic", "Test", "India,MP,Khandwa", "21.8333, 76.3667", "123459", "cid004"],
        ["Jabalpur Clinic", "Test", "India,MP,Jabalpur", "23.2, 79.95", "123458", "cid003"],
        ["Satna Clinic", "Test", "India,MP,Satna", "24.5667, 80.8333", "123457", "cid002"],
        ["Clinic", "Antsirabe", "ANTSIRABE,AMBANJA,DIANA,Madagascar", "-19.8167, 47.0667", "87654326", "cli13"]
    ], "iTotalDisplayRecords": 18, "iDisplayStart": 0, "iDisplayLength": 10}};

    var respose_25_datarows = {responseText: {"iTotalRecords": 25, "data": [
        ["Clinic", "TSIMANARIRAZANA", "TSIMANARIRAZANA,ANDRAINJATO AVARATRA,FIANARANTSOA I,HAUTE MATSIATRA,Madagascar", "-12.35, 49.3", "87654325", "cli12"],
        ["Clinic", "Antalaha", "ANTALAHA,SAVA,Madagascar", "-14.8833, 50.25", "87654323", "cli10"],
        ["Clinic", "ANALAMANGA", "ANALAMANGA,Madagascar", "-18.8, 47.4833", "87654324", "cli11"],
        ["Kochi Clinic", "Test", "India,Kerala,Kochi", "9.939248, 76.259625", "123460", "cid005"],
        ["New Gwalior Clinic", "Test", "India,Madhya Pradesh,New Gwalior", "26.227112, 78.18708", "1234561", "cid006"],
        ["Indore Clinic", "Test", "India,Madhya Pradesh,Indore", "22.7167, 75.8", "1234562", "cid007"],
        ["Khandwa Clinic", "Test", "India,MP,Khandwa", "21.8333, 76.3667", "123459", "cid004"],
        ["Jabalpur Clinic", "Test", "India,MP,Jabalpur", "23.2, 79.95", "123458", "cid003"],
        ["Satna Clinic", "Test", "India,MP,Satna", "24.5667, 80.8333", "123457", "cid002"],
        ["Clinic", "Antsirabe", "ANTSIRABE,AMBANJA,DIANA,Madagascar", "-19.8167, 47.0667", "87654326", "cli13"],
        ["Clinic", "Besalampy", "BESALAMPY,MELAKY,Madagascar", "-16.75, 44.5", "87654327", "cli14"],
        ["Clinic", "Analalava", "ANALALAVA,SOFIA,Madagascar", "-14.6333, 47.7667", "987654321", "cli8"],
        ["Clinic", "Farafangana", "FARAFANGANA,ATSIMO ATSINANANA,Madagascar", "-22.8, 47.8333", "87654328", "cli15"],
        ["Clinic", "Mahajanga", "MAHAJANGA,MAHAJANGA I,BOENY,Madagascar", "-15.6667, 46.35", "87654331", "cli18"],
        ["Clinic", "Andapa", "ANDAPA,SAVA,Madagascar", "-14.65, 49.6167", "87654322", "cli9"],
        ["Clinic", "Fianarantsoa-I", "Fianarantsoa-I", "-21.45, 47.1", "87654329", "cli16"],
        ["Clinic", "Sainte-Marie", "Sainte-Marie", "-17.0833, 49.8167", "87654330", "cli17"],
        ["Bhopal Clinic", "Test", "India,MP,Bhopal", "23.2833, 77.35", "123456", "cid001"],
        ["Clinic", "TSIMANARIRAZANA", "TSIMANARIRAZANA,ANDRAINJATO AVARATRA,FIANARANTSOA I,HAUTE MATSIATRA,Madagascar", "-12.35, 49.3", "87654325", "cli12"],
        ["Clinic", "Antalaha", "ANTALAHA,SAVA,Madagascar", "-14.8833, 50.25", "87654323", "cli10"],
        ["Clinic", "ANALAMANGA", "ANALAMANGA,Madagascar", "-18.8, 47.4833", "87654324", "cli11"],
        ["Kochi Clinic", "Test", "India,Kerala,Kochi", "9.939248, 76.259625", "123460", "cid005"],
        ["New Gwalior Clinic", "Test", "India,Madhya Pradesh,New Gwalior", "26.227112, 78.18708", "1234561", "cid006"],
        ["Indore Clinic", "Test", "India,Madhya Pradesh,Indore", "22.7167, 75.8", "1234562", "cid007"],
        ["Khandwa Clinic", "Test", "India,MP,Khandwa", "21.8333, 76.3667", "123459", "cid004"]
    ], "iTotalDisplayRecords": 25, "iDisplayStart": 0, "iDisplayLength": 25}};


    beforeEach(function () {
        jasmine.getFixtures().set('<div id="table-wrapper"><table id="simpleTable" ><thead><tr></tr></thead></table></div>');
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
    });

    it('should find Select a Subject as menu item when no row is selected', function () {
        $($.find('button')[0]).trigger('click');
        expect($('.dropdown ul li.none-selected').text()).toEqual('Select a Subject');
        $($.find('button')[0]).trigger('click')
    });

    it('should find Select all link when all rows in the page are selected', function () {
        var table = $("#simpleTable_wrapper");
        select_all_rows(table);
        expect(table.find('.table_wrapper .select_all_message').text()).toEqual("You have selected 10 Subject(s) on this page. Select all  30 Subject(s)")
    });

    it('should find Clear all link when Select all is clicked and should disappear when Clear Selection is clicked', function () {
        var table = $("#simpleTable_wrapper");
        select_all_rows(table);
        table.find('.select_all_message a').click();
        expect(table.find('.select_all_message').text()).toEqual('You have selected all 30 Subject(s). Clear Selection');

        table.find('.select_all_message a').click();
        expect(table.find('tbody tr:first')).toBeHidden();
    });

    it('should not find Select all>all when number of rows are less than page size', function () {
        var table = $("#simpleTable_wrapper");
        var pagesize = 50;
        change_page_size_to(pagesize);
        select_all_rows(table);
        expect(table.find('tbody tr:first')).toBeHidden();
    });

    it('should verify number of table rows and pagination text when page size is changed', function () {
        var table = $("#simpleTable_wrapper");
        verifyInitialState(table);

        var pagesize = 50;
        change_page_size_to(pagesize);
        expect(table.find('.row_checkbox')).toHaveLength(30);
        expect(table.find('.dataTables_info').first()).toHaveText('1 to 30 of 30 Subject(s)');

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
        var table = $("#simpleTable_wrapper");
        var previous_page_button = table.find('.paginate_disabled_previous:first');
        expect(previous_page_button).not.toBeNull();
        table.find('.paginate_enabled_next:first').click();
        expect(table.find('.dataTables_info').first()).toHaveText('11 to 20 of 30 Subject(s)');
    });


    it('should check visibility of pagination first and last buttons', function () {
        var table = $("#simpleTable_wrapper");
        table.find('.paginate_more:first').click();

        expect(getPaginationButton("first_page").parent()).toHaveAttr('class', 'disabled');

        getPaginationButton("last_page").click();
        expect(table.find('.dataTables_info').first()).toHaveText('21 to 30 of 30 Subject(s)');

        table.find('.paginate_more:first').click();
        expect(getPaginationButton("last_page").parent()).toHaveAttr('class', 'disabled');
        expect(getPaginationButton("first_page").parent()).not.toHaveAttr('class', 'disabled');
        table.find('.paginate_more:first').click();
    });

    function verifyInitialState(table) {
        expect(table.find('.dataTables_info').first()).toHaveText('1 to 10 of 30 Subject(s)');
        expect(table.find('.row_checkbox')).toHaveLength(10);
    }

    function getPaginationButton(pagination_link) {
        var pagination_button;
        $("div[id*='pagination_more_menu']").each(function () {
            if (($(this).attr('style')) != 'display:none;') {
                pagination_button = $(this).find($("a[id*='" + pagination_link + "']"));
            }
        });
        return pagination_button;
    }

    function select_all_rows(table) {
        var checkallBox = table.find('.checkall-checkbox');
        // click handler is called before the checked value is updated; so setting checked value explicitly
        checkallBox.prop('checked', true);
        checkallBox.click();
        // the above click makes the checked value false; manually setting to true
        checkallBox.prop('checked', true);
    }

    function change_page_size_to(page_size) {
        $('#simpleTable_length select').val(page_size).change()
    }

});
