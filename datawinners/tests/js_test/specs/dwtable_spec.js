describe("dwtable", function() {

    var TestResponses = {
      search: {
        success: {
          status: 200,
          responseText: {"iTotalRecords": 18, "data": [["Clinic", "TSIMANARIRAZANA", "TSIMANARIRAZANA,ANDRAINJATO AVARATRA,FIANARANTSOA I,HAUTE MATSIATRA,Madagascar", "-12.35, 49.3", "87654325", "cli12"], ["Clinic", "Antalaha", "ANTALAHA,SAVA,Madagascar", "-14.8833, 50.25", "87654323", "cli10"], ["Clinic", "ANALAMANGA", "ANALAMANGA,Madagascar", "-18.8, 47.4833", "87654324", "cli11"], ["Kochi Clinic", "Test", "India,Kerala,Kochi", "9.939248, 76.259625", "123460", "cid005"], ["New Gwalior Clinic", "Test", "India,Madhya Pradesh,New Gwalior", "26.227112, 78.18708", "1234561", "cid006"], ["Indore Clinic", "Test", "India,Madhya Pradesh,Indore", "22.7167, 75.8", "1234562", "cid007"], ["Khandwa Clinic", "Test", "India,MP,Khandwa", "21.8333, 76.3667", "123459", "cid004"], ["Jabalpur Clinic", "Test", "India,MP,Jabalpur", "23.2, 79.95", "123458", "cid003"], ["Satna Clinic", "Test", "India,MP,Satna", "24.5667, 80.8333", "123457", "cid002"], ["Clinic", "Antsirabe", "ANTSIRABE,AMBANJA,DIANA,Madagascar", "-19.8167, 47.0667", "87654326", "cli13"]], "iTotalDisplayRecords": 18, "iDisplayStart": 0, "iDisplayLength": 10}
        }
      }
    };


    beforeEach(function (){
        jasmine.getFixtures().set('<div id="table-wrapper"><table id="simpleTable" ><thead><tr></tr></thead></table></div>');
        setupSpyForTableData();

        $("#simpleTable").dwTable({
            "concept":"Subject",
            "sAjaxSource": '/entity/subjects/clinic/ajax/',
            "sAjaxDataIdColIndex": 6,
            "iDisplayLength": 10,
            "bServerSide": true
            ,"actionItems" : [ {"label": "Delete", handler:function(tb){alert('delete' + tb);}, "allow_selection": "multiple"},
                              {"label":"Edit", handler:function(){alert('edit');}, "allow_selection": "single"}
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

    it('should find Select a Subject as menu item when no row is selected', function() {
        $($.find('button')[0]).trigger('click')
        expect($('.dropdown ul li.none-selected').text()).toEqual('Select a Subject');
        $($.find('button')[0]).trigger('click')
    });

    it('should find Select all link when all rows in the page are selected', function() {
        var table_object = $("#simpleTable_wrapper");
        select_all_rows(table_object);
        expect(table_object.find('.table_wrapper .select_all_message').text()).toEqual("You have selected 10 Subject(s) on this page. Select all  18 Subject(s)")
    });

    function select_all_rows(table_object) {
        var checkallBox = table_object.find('.checkall-checkbox');
        // click handler is called before the checked value is updated; so setting checked value explicitly
        checkallBox.prop('checked', true);
        checkallBox.click();
        // the above click makes the checked value false; manually setting to true
        checkallBox.prop('checked', true);
    }

    function setupSpyForTableData() {
        spyOn(jQuery, "ajax").andCallFake(function(params) {
            params.success(TestResponses.search.success.responseText);
        });
    }
});