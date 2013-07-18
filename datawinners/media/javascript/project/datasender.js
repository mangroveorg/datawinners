$(document).ready(function(){

    $(".add_datasender_form").dialog({
       autoOpen: false,
       width: 575,
       modal: true,
       title: gettext('Add a Data Sender'),
       close: function() {

           $('.errorlist').remove();
           $('#error_messages').remove();
           $("#id_first_name").parent().removeClass("error");
           $("#id_telephone_number").parent().removeClass("error");
           $("#id_location").parent().removeClass("error");
           $("#id_geo_code").parent().removeClass("error");
           $("#flash-message").remove();
           $('#registration_form')[0].reset();
       }
   });


   $("#add_datasenders").unbind('click').click(function() {
       $(".add_datasender_form").dialog("open");
   });
   
   $(".cancel_link").live("click", function(event){
       event.preventDefault();
       $(".add_datasender_form").dialog("close");
   });


});
