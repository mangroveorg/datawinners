describe("Import Submission Popup", function(){

    beforeEach(function(){
        setFixtures("<a class='import_link' data-projectname='projectname123' data-filename='filename' \
            data-formcode='formcode123' data-projectid='999909b65b0'></a><a id='template-download-link'></a>\
            <a id='secondary-template-download-link'></a>\
            <div id='submission_import'></div>")
    });

    it("should update download and upload links from data attributes of selected project questionnare import link", function(){
        var options = {
        "import_template_url_template": '/domain/project/subject/form_code?filename=<project_name>',
        "import_submission_url_template": '/domain/project/import-submissions/form_code'
    };
        var popup = new DW.SubmissionImportPopup().init(options);

        popup.updateUrls($(".import_link"));

        expect($("#template-download-link")).toHaveAttr("href", "/domain/project/subject/formcode123?filename=projectname123")
        expect(popup.upload_link).toEqual("/domain/project/import-submissions/formcode123?project_id=999909b65b0")
    });

    it("should show dialog when popup is opened", function(){
        spyOn(window, "gettext").andReturn("someText");
        var chainedDialogSpy = jasmine.createSpy("chainedDialog");
        var mockDialog = spyOn($.fn, "dialog").andReturn({
            "dialog": chainedDialogSpy
        });
        var popup = new DW.SubmissionImportPopup().init({});

        popup.open();

        expect(mockDialog).toHaveBeenCalled();
        expect(chainedDialogSpy).toHaveBeenCalledWith("open")
    });

    it("should update the primary and secondary download template link text with filename from data attribute",function(){
        var options = {
        "import_template_url_template": '/domain/project/subject/form_code?filename=<project_name>',
        "import_submission_url_template": '/domain/project/import-submissions/form_code'
    };
        var popup = new DW.SubmissionImportPopup().init(options);

        popup.updateTemplateFileName($(".import_link"));

        expect($("#template-download-link")).toHaveText("filename.xlsx")
        expect($("#secondary-template-download-link")).toHaveText("filename.xlsx")
    })
});
