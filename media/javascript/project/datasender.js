$(document).ready(function(){

    $(".add_datasender_form").dialog({
       autoOpen: false,
       width: 575,
       modal: true,
       title: 'Add a data sender',
       close: function() {
           $('#message').remove();
           $('#question_form').each (function(){
             this.reset();
           });
//           DW.validator.resetForm();
       }
   });


   $("#add_datasenders").unbind('click').click(function() {
       $(".add_datasender_form").dialog("open");
   });


});
