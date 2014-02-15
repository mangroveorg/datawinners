describe("subject import", function(){

    beforeEach(function(){
        loadFixtures("subjects_import_popup_fixture.html");
    });

    describe("when all subject rows are successfully imported", function(){

        var response;

        beforeEach(function(){
            response = {
                success: true,
                message: "3 of 3 records successfully imported",
                failure_imports: [],
                successful_imports: [
                                        ["sub1_val1", "sub1_val2", "sub1_val3"],
                                        ["sub2_val1", "sub2_val2", "sub2_val3"]
                                    ]
            };

        });

        it("should show successfully imported subject rows in the success table", function(){
            expect($("#subject_success_table")).toBeHidden();
            expect($("#subject_success_table tbody tr")).not.toExist();

            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#subject_success_table tbody  tr")).toExist();
            expect($("#subject_success_table tbody  tr").length).toEqual(2);
            expect($("#subject_success_table tbody  tr")[0]).toContainHtml("<td>sub1_val1</td><td>sub1_val2</td><td>sub1_val3</td>")
            expect($("#subject_success_table tbody  tr")[1]).toContainHtml("<td>sub2_val1</td><td>sub2_val2</td><td>sub2_val3</td>")
            expect($("#subject_success_table")).toBeVisible();
        });

        it("should not show the errored table", function(){
            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#subject_error_table")).toBeHidden();
        });

        it("should show the count of all records successfully imported", function(){
            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#message")).toContainText("3 of 3 records successfully imported");
            expect($("#message")).toBeMatchedBy(".success_message");
            expect($("#message")).toBeMatchedBy(".success-message-box");
        });

    });

    describe("when all subject rows fail to be imported", function(){

        var response;

        beforeEach(function(){
             response = {
                success: false,
                message: "0 of 2 records successfully imported",
                failure_imports: [
                                    {row_num: 2, error: "Error message1"},
                                    {row_num: 3, error: "Error message2"}
                                 ],
                successful_imports: []
            };
        });

        it("should show the errored row number and the failure message", function(){
            expect($("#subject_error_table")).toBeHidden();
            expect($("#subject_error_table tbody tr")).not.toExist();

            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#subject_error_table tbody  tr")).toExist();
            expect($("#subject_error_table tbody  tr").length).toEqual(2);
            expect($("#subject_error_table tbody  tr")[0]).toContainHtml("<td>2</td><td>Error message1</td>")
            expect($("#subject_error_table tbody  tr")[1]).toContainHtml("<td>3</td><td>Error message2</td>")
            expect($("#subject_error_table")).toBeVisible();
        });

        it("should not show the success table", function(){
            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#subject_success_table")).toBeHidden();
        });

        it("should show the count of all records that failed to be imported", function(){
            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#message")).toContainText("0 of 2 records successfully imported");
            expect($("#message")).toBeMatchedBy(".error_message");
            expect($("#message")).toBeMatchedBy(".message-box");
        });

    });


    describe("when there is a combination of failed and successful imports", function(){

        var response;

        beforeEach(function(){
             response = {
                success: false,
                failure_imports: [
                                    {row_num: 3, error: "Error message1"}
                                 ],
                successful_imports: [
                                        ["sub1_val1", "sub1_val2", "sub1_val3"],
                                    ]
            };
        });

        it("should show the errored row number and the failure message", function(){
            expect($("#subject_error_table")).toBeHidden();
            expect($("#subject_error_table tbody tr")).not.toExist();

            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#subject_error_table tbody  tr")).toExist();
            expect($("#subject_error_table tbody  tr").length).toEqual(1);
            expect($("#subject_error_table tbody  tr")[0]).toContainHtml("<td>3</td><td>Error message1</td>")
            expect($("#subject_error_table")).toBeVisible();
        });

       it("should show successfully imported subject rows in the success table", function(){
            expect($("#subject_success_table")).toBeHidden();
            expect($("#subject_success_table tbody tr")).not.toExist();

            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#subject_success_table tbody  tr")).toExist();
            expect($("#subject_success_table tbody  tr").length).toEqual(1);
            expect($("#subject_success_table tbody  tr")[0]).toContainHtml("<td>sub1_val1</td><td>sub1_val2</td><td>sub1_val3</td>")
            expect($("#subject_success_table")).toBeVisible();
        });

    });

    describe("when an unexpected error occurs", function(){

        var response;

        beforeEach(function(){
             response = {
                success: false,
                error_message: "Some unfortunate error occurred",
                failure_imports: [],
                successful_imports: []
            };
        });

        it("should show the error message", function(){
            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#message")).toContainText("Some unfortunate error occurred");
            expect($("#message")).toBeMatchedBy(".error_message");
            expect($("#message")).toBeMatchedBy(".message-box");
        });

        it("should neither show the success nor error table", function(){
            expect($("#subject_success_table")).toBeHidden();
            expect($("#subject_error_table")).toBeHidden();

            DW.SubjectImportResponseHandler("id", "fileName", response);

            expect($("#subject_success_table")).toBeHidden();
            expect($("#subject_error_table")).toBeHidden();
        });

    });


});


