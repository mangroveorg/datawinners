$(function () {

    new DW.UploadQuestionnaire({
        buttonText: "Upload New XLSForm",
        postUrl: function(){
           return '/xlsform/upload/update/'+ project_id +'/';
        },
        postSuccessSave: function(responseJSON){
            var flash_message = $("#xlx-error-message");
            flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box").
            html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
            $('#message-label').delay(5000).fadeOut();
        }
    });

    $('.download_link').click(function(){
        $('#download_form').attr('action', '/xlsform/download/').submit();
    });
});
