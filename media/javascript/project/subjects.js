$(document).ready(function() {
    $("#question-detail-panel > div").hide();
    $('.question_list ol > div:first').toggleClass("question_selected");
    $('.question_list ol > div:first').find(".selected_question_arrow").show();
    $("#question-detail-panel > div.answer1").show();

    $('.question_list ol > div').live("click", function() {
        $("#question-detail-panel > div").hide();
        $('.question_list ol > div').removeClass("question_selected")
        $('.question_list ol > div li span.selected_question_arrow').hide()
        $(this).toggleClass("question_selected");
        $(this).find(".selected_question_arrow").show();

        var question_class = $(this).attr('class').match(/question[0-9]+/);
        var answer_class = question_class[0].replace(/question/, "answer");
        $("#question-detail-panel > div." + answer_class).show();
    });
    $(".add_subject_form").dialog({
        autoOpen: false,
        width: 500,
        modal: true,
        title: 'Add a subject',
        close: function() {
            $('#message').remove();
            $('#question_form').each (function(){
              this.reset();
            });
            DW.validator.resetForm();
        }
    });

    $("#add_subject").unbind('click').click(function() {
        $(".add_subject_form").dialog("open");
    });
    $("#import_subjects").unbind('click').click(function() {
        $(".import_subject_form").dialog("open");
    });
    $(".import_subject_form").dialog({
        autoOpen: false,
        width: 500,
        modal: true,
        title: 'Import a List',
        close: function() {
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
        }
    });
    $('#register_entity').unbind('click').click(function() {
        if ($('#question_form').valid()) {
            var message = {'form_code':'reg',
                't':$('#id_entity_type').val(),
                's':$('#short_name').val(),
                'l':$('#location').val(),
                'd':$('#description').val(),
                'm':$('#mobile_number').val(),
                'n':$('#entity_name').val(),
                'g':$('#geo_code').val()
            }
            var data = {'message':message,'transport': 'web','source': 'web','destination': 'mangrove'}
            $.post('/submit', {'format': 'json', 'data': JSON.stringify(data, null, 1)},
                    function(response) {
                        var d = JSON.parse(response);
                        $('#message').remove();
                        if (d.success) {
                            $('<span id="message" class="success_message">' + d.message + '</span>').insertBefore($('#question_form'));
                            $('#message').delay(10000).fadeOut();
                        }
                        else {
                            $('<span id="message" class="error_message">' + d.message + '</span>').insertBefore($('#question_form'));
                        }
                    }
            );
        }
    }
    );
    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element: document.getElementById('file_uploader'),
        // path to server-side upload script
        action: $('#post_url').val(),
        onComplete: function(id, fileName, responseJSON) {
            $('#message').remove();
            if (responseJSON.success == true) {
                $('<span id="message" class="success_message">' + responseJSON.message + '</span>').insertAfter($('#file-uploader'));
            }
            else {
                $('<span id="message" class="error_message">' + responseJSON.message + '</span>').insertAfter($('#file-uploader'));
                $.each(responseJSON.failure_imports, function(index, element) {
                    var row = '';
                    $.each(element.row, function(i, e) {
                        row = row + " " + e + ","
                    });
                    $("#error_table table tbody").append("<tr><td>" + element.row_num + "</td><td>" + row + "</td><td>"
                            + element.error + "</td></tr>")
                    $("#error_table").show();
                })
            }
        }
    });

    $("#file_uploader input").addClass("button");

});
