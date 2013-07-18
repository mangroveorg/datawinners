$(document).ready(function() {
    $("#error_table").hide();
    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element: document.getElementById('file_uploader'),
        // path to server-side upload script
        action: window.location.pathname,
        onComplete: function(id, fileName, responseJSON) {
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
            $("#subject_table tbody").html('');
            $.each(responseJSON.all_data, function(index, element) {
                $("#subject_table tbody").append("<tr>" +
                        "<td>" + element.short_name + "</td>" +
                        "<td>" + element.name + "</td>" +
                        "<td>"  + element.type + "</td>" +
                        "<td>" + element.location + "</td>" +
                        "<td>"+ element.geocode + "</td>" +
                        "<td>" + element.description + "</td>" +
                        "<td>" + element.mobile_number + "</td></tr>");
            });
            if (responseJSON.success == true) {
                $('<div id="message" class="success_message success-message-box">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));

            }
            else {
                $('#error_tbody').html('');
                if (responseJSON.error_message)
                {
                    $('<div id="message" class="error_message message-box">' + responseJSON.error_message + '</div>').insertAfter($('#file-uploader'));
                }
                else{
                    $('<div id="message" class="error_message message-box">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));
                }
                if(responseJSON.failure_imports > 0)
                {
                    $("#error_table").show();
                }
                $.each(responseJSON.failure_imports, function(index, element) {
                    $("#error_table table tbody").append("<tr><td>" + element.row_num + "</td><td>" + JSON.stringify(element.row) + "</td><td>"
                            + element.error + "</td></tr>");
                });
                $("#error_table").show();
            }

        }
    });


});

function getEntityIdsToBeDeleted(action_element) {
    var entity_code = $(action_element).attr('data-entity').split('-')[1];
    var allIds = [];
    var tbody_id = entity_code + "-table";
    $('#' + tbody_id + ' :checked').not(".checkall-subjects").each(function () {
        allIds.push($(this).val());
    });
    return allIds;
}

function getEntityType(action_element){
    return $(action_element).attr('data-entity').split('-')[0];
}
function getEditURL(){
    return edit_url;// current page is All Subjects Page
}

function getActionValue(action_element){
    var separated_values = $(action_element).attr('data-entity').split('-');
    return separated_values[separated_values.length-1];
}