describe("Import Submission postupload", function(){
    var success_table;
    var fileUploader;

    beforeEach(function(){
         setFixtures('<div id="file_uploader"></div> \
            <div id="success_import_section" class="import_section"> \
                <div id="success_table_message" class="import_message"></div> \
                <div class="import_table"> \
                    <table id="success_table" class="styled_table"></table>\
                </div> \
            </div>');

         success_table = $('#success_table');
         $.unblockUI = function (){};
        fileUploader = new DW.SubmissionFileUploader({});
    });
    it("should update the success table header on success submission", function(){
        var responseJSON = {
            'question_map':{'q1':'question_1', 'q2':'question_2'},
            'success_submissions':[{'q1':'answer_1'},{'q2':'answer_2'}]
        };

        fileUploader.onComplete('', '', responseJSON);

        expect(success_table.find('thead tr th').length).toEqual(2);
        expect(success_table.find('thead tr th')[0]).toContainText('question_1');
        expect(success_table.find('thead tr th')[1]).toContainText('question_2');
    });

    it("should update body with successful submissions", function(){
        var responseJSON = {
            'question_map':{'q1':'question_1', 'q2':'question_2'},
            'success_submissions':[{'q1':'answer_11','q2':'answer_12'}, {'q1':'answer_21','q2':'answer_22'}]
        };

        fileUploader.onComplete('', '', responseJSON);

        expect(success_table.find('tbody tr').length).toEqual(2);
        var first_row = success_table.find('tbody tr').first().find('td');
        expect(first_row.length).toEqual(2);
        var second_row = success_table.find('tbody tr').last().find('td');
        expect(second_row.length).toEqual(2);
        expect(first_row[0]).toContainText("answer_11");
        expect(first_row[1]).toContainText("answer_12");
        expect(second_row[0]).toContainText("answer_21");
        expect(second_row[1]).toContainText("answer_22");
    });

    it("should hide onload spinner when upload completes", function() {
        var mockedUiblockUI = spyOn($, 'unblockUI');

        fileUploader.onComplete('', '', {'success_submissions':[]});

        expect(mockedUiblockUI).toHaveBeenCalled();
    });

});
