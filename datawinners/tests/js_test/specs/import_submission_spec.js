describe("Import Submission Popup", function(){

    beforeEach(function(){
        setFixtures("<a class='import_link' data-projectname='projectname123' \
            data-formcode='formcode123'></a><a id='template-download-link'></a>\
            <div id='submission_import'></div>")
    });

    it("should create template download link url from data attributes of selected project questionnare import link", function(){
        var popup = new DW.SubmissionImportPopup().init("/domain/project/subject/form_code?filename=<project_name>");

        popup.updateTemplateDownloadLink($(".import_link"));

        expect($("#template-download-link")).toHaveAttr("href", "/domain/project/subject/formcode123?filename=projectname123")
    });

    it("should show dialog when popup is opened", function(){
        spyOn(window, "gettext").andReturn("someText");
        var chainedDialogSpy = jasmine.createSpy("chainedDialog");
        var mockDialog = spyOn($.fn, "dialog").andReturn({
            "dialog": chainedDialogSpy
        });
        var popup = new DW.SubmissionImportPopup().init("/domain/project/subject/form_code?filename=<project_name>");

        popup.open();

        expect(mockDialog).toHaveBeenCalled();
        expect(chainedDialogSpy).toHaveBeenCalledWith("open")
    });

});
