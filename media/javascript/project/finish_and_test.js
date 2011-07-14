$(document).ready(function(){
$("#project_profile").accordion({   alwaysOpen: false, collapsible: true,autoHeight:false});
$("#subjects").accordion({   alwaysOpen: false, collapsible: true,autoHeight:true, active: false});
$("#questionnaire").accordion({   alwaysOpen: false, active: false,collapsible: true,autoHeight:false});
$("#data_senders").accordion({   alwaysOpen: false, active: false,collapsible: true,autoHeight:false});
    $(".sms_tester_form").dialog({
       autoOpen: false,
       width: 600,
       modal: true,
       title: 'SMS Tester'
//       close: function() {
//
//           $('.errorlist').remove();
//           $('#error_messages').remove();
//           $("#id_first_name").parent().removeClass("error");
//           $("#id_telephone_number").parent().removeClass("error");
//           $("#id_location").parent().removeClass("error");
//           $("#id_geo_code").parent().removeClass("error");
//           $("#flash-message").remove();
//           $('#registration_form')[0].reset();
//       }
   });
       $("#sms_tester").unbind('click').click(function() {
       $(".sms_tester_form").dialog("open");
   });

    $("#send_sms").unbind('click').click(function(){
        $.post('/submission',{'from_msisdn':$("#from_msisdn").val(), 'to_msisdn':$("#to_msisdn").val(), 'message':$("#id_message").val()}, function(response){
                    $("#id_message").val(response);
                });
    });
    $(".questionnaire_preview").dialog({
            title: "Questionnaire Preview",
            modal: true,
            autoOpen: false,
            height: 700,
            width: 800,
            closeText: 'hide',
            open: function() {
              // Here I load the content. This is the content of your link.
              $(".questionnaire_preview").load(quessionarie_preview_link, function() {});
            }
          }
      );
    $(".preview").bind("click", function(){
       $(".questionnaire_preview").dialog("open");
    })
});