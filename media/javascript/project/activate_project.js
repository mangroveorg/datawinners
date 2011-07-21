$(document).ready(function(){
   $(".activate_project").bind("click", function(){
       var redirect = confirm("Warning: Activating the project will remove all existing test data (if any).");
       return redirect;
   })
});
