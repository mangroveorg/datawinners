$(document).ready(function() {
    $("#id_register_button").unbind().live('click', function() {
//       event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/entity/datasender/create',
            data: $("#registration_form").serialize(),
            success:function(response) {
                $("#add_data_sender_form").html(response);
                $("#id_location").autocomplete("/places", {
                    minChars: 0,
                    max: 12,
                    autoFill: true,
                    mustMatch: true,
                    matchContains: false,
                    scrollHeight: 220});
            },
            error: function(e){
                $("#message-label").show().html("<label class='error_message'>" + e.responseText + "</label>");
            }

        });
    });

    $("#id_location").autocomplete("/places", {
        minChars: 0,
        max: 12,
        autoFill: true,
        mustMatch: true,
        matchContains: false,
        scrollHeight: 220});

});