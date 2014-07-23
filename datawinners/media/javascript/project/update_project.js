
$(function() {
    new qq.FileUploader({
        element: document.getElementById('file_uploader'),
        action: '/xlsform/upload/update/'+ project_id +'/',
        params: {},
        onSubmit: function () {
            if(confirm("Submission related to existing project will be deleted"))
                $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
            else
                window.location.replace('/project/overview/' + responseJSON.project_id +'/');
        },
        onComplete: onComplete
    });
});

function onComplete(id, fileName, responseJSON){
    $.unblockUI();
    if (responseJSON['error_msg']) {
        alert(responseJSON['error_msg']);
    } else {
        alert('Project updated: ' + responseJSON.project_name);
//        update_table(responseJSON.xls_dict)
//        window.location.replace('/project/overview/' + responseJSON.project_id +'/');
    }
}