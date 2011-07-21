$(document).ready(function(){
   $(".activate_project").bind("click", function(){
       var redirect = confirm("Are you sure?" +
               "\nThis will activate the project and delete the submissions made if any");
       return redirect;
   })
});
