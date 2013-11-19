describe("My DataSenders Table", function() {

    var onSuccess, onFailure;
    var serviceUrl;
    var TestResponses = {
      search: {
        success: {
          status: 200,
          responseText: {"iTotalRecords": 18, "data": [["Clinic", "TSIMANARIRAZANA", "TSIMANARIRAZANA,ANDRAINJATO AVARATRA,FIANARANTSOA I,HAUTE MATSIATRA,Madagascar", "-12.35, 49.3", "87654325", "cli12"], ["Clinic", "Antalaha", "ANTALAHA,SAVA,Madagascar", "-14.8833, 50.25", "87654323", "cli10"], ["Clinic", "ANALAMANGA", "ANALAMANGA,Madagascar", "-18.8, 47.4833", "87654324", "cli11"], ["Kochi Clinic", "Test", "India,Kerala,Kochi", "9.939248, 76.259625", "123460", "cid005"], ["New Gwalior Clinic", "Test", "India,Madhya Pradesh,New Gwalior", "26.227112, 78.18708", "1234561", "cid006"], ["Indore Clinic", "Test", "India,Madhya Pradesh,Indore", "22.7167, 75.8", "1234562", "cid007"], ["Khandwa Clinic", "Test", "India,MP,Khandwa", "21.8333, 76.3667", "123459", "cid004"], ["Jabalpur Clinic", "Test", "India,MP,Jabalpur", "23.2, 79.95", "123458", "cid003"], ["Satna Clinic", "Test", "India,MP,Satna", "24.5667, 80.8333", "123457", "cid002"], ["Clinic", "Antsirabe", "ANTSIRABE,AMBANJA,DIANA,Madagascar", "-19.8167, 47.0667", "87654326", "cli13"]], "iTotalDisplayRecords": 18, "iDisplayStart": 0, "iDisplayLength": 10}
        }
      }
    };
    var deleteSpyedHandler, editSpyedHandler;

    function setupSpyForTableData() {
        spyOn(jQuery, "ajax").andCallFake(function(params) {
            params.success(TestResponses.search.success.responseText);
        });
    }

    beforeEach(function (){
        jasmine.getFixtures().set('<div id="table-wrapper"><table id="simpleTable" ><thead><tr></tr></thead></table></div>');

        onSuccess = jasmine.createSpy('onSuccess');
        onFailure = jasmine.createSpy('onFailure');
        serviceUrl = '/entity/subjects/clinic/ajax/';

        setupSpyForTableData();

        deleteSpyedHandler = jasmine.createSpy();
        editSpyedHandler = jasmine.createSpy();
        var table_page_size = 10;

        $("#simpleTable").dwTable({
            "concept":"Subject",
            "sAjaxSource": serviceUrl,
            "sAjaxDataIdColIndex": 6,
            "iDisplayLength":table_page_size,
            "bServerSide": true
            ,"actionItems" : [ {"label": "Delete", handler:deleteSpyedHandler, "allow_selection": "multiple"},
                              {"label":"Edit", handler:editSpyedHandler, "allow_selection": "single"}
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

    it('should find delete handler called', function() {
        var table_object = $("#simpleTable_wrapper");
        clickFirstRowCheckBox(table_object);
        clickActionButton(table_object);
        clickMenuItem(".delete");
        expect(deleteSpyedHandler).toHaveBeenCalled();
    });

    // seems some issue with the spying
//    it('should find edit called', function() {
//        var table_object = $("#simpleTable_wrapper");
//        clickFirstRowCheckBox(table_object);
//        clickActionButton(table_object);
//        clickMenuItem(".edit");
//        expect(editSpyedHandler).toHaveBeenCalled();
//    });

    function clickActionButton(table) {
        table.find('.table_action_button').first().find('button').click();
    }

    function clickMenuItem(menuItemClass) {
        $('.dropdown ul li a' + menuItemClass).click();
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