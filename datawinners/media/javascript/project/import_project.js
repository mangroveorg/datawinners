
$(function() {
    new qq.FileUploader({
        element: document.getElementById('file_uploader'),
        action: '/xlsform/upload/',
        params: {},
        buttonText: "Upload XLSForm and create Questionnaire",
        onSubmit: function () {
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
        },
        onComplete: onComplete
    });
});
function onComplete(id, fileName, responseJSON){
    $.unblockUI();
    if (responseJSON['error_msg']) {
        alert(responseJSON['error_msg']);
    } else {
        alert('Project created: ' + responseJSON.project_name);
        window.location.replace('/project/overview/' + responseJSON.project_id +'/');
    }

}
