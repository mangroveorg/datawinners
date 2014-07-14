$(function () {

    new DW.UploadQuestionnaire({
        buttonText: "Upload New XLSForm",
        postUrl: function(){
           return '/xlsform/upload/update/'+ project_id +'/';
        },
        postErrorHandler: function(responseJSON) {
            DW.showError(responseJSON['error_msg']);
        }

    });

    $('.download_link').click(function(){
        $('#download_form').attr('action', '/xlsform/download/').submit();
    });
});
