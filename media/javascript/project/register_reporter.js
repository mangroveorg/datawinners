$(document).ready(function(){
$("#id_register_button").unbind().click(function(){
//       event.preventDefault();
       $.ajax({
            type: 'POST',
            url: '/reporter/register_via_ajax/',
            data: $("#registration_form").serialize(),
                    success:function(response) {
                       $("#add_data_sender_form").empty();
                       $("#add_data_sender_form").append(response);
                    }
       });
       })
        var data = ["india", "japan", "america"]
    $("#id_location").autocomplete("/places", {
		minChars: 0,
		max: 12,
		autoFill: true,
		mustMatch: true,
		matchContains: false,
		scrollHeight: 220});

});