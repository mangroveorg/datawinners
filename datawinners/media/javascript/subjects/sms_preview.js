DW = DW || {};

$(document).ready(function () {
    var sms_view_page = new DW.SubjectSMSPreviewPage();
    var registration_form = new DW.SubjectRegistrationForm("#subject_registration_form");
    new DW.SubjectViewStyleButtons(sms_view_page, registration_form);
    var modal_page = new DW.SubjectPrintModalPage();

    $(".preview_subject_registration_form").bind("click", function (eventObject) {
        modal_page.display();
        return false;
    });
});
