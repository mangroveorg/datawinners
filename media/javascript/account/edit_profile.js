$(document).ready(function() {
   $('#id_username').attr('disabled',true);

   $('#form_submit').click(function(){
      $('#id_username').attr('disabled',false);
      $('#profile_form').submit();
   });
});