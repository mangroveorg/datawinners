$(document).ready(function(){
  $('#user_form').hide();
  $('#return_to_users_list').hide();
  
  $('#add_users').click(function(){
    $('#add_users').hide();
    $('#users_list').hide();
    $('#user_form').show();
    $('#return_to_users_list').show();
  });
  
  $('#return_to_users_list').click(function(){
    $('#add_users').show();
    $('#users_list').show();
    $('#user_form').hide();
    $('#return_to_users_list').hide();
  });
  
});
