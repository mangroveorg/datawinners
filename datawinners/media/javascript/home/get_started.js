$(document).ready(function(){
   function active_step(number){
       $(".get-started-step").hide();
       $("#next-step, #prev-step").show();
       $(".get-started-step").eq(number).show();

       var length = $(".get-started-step").length;
       if(number >= length-1)
           $("#next-step").hide();

       if(!number)
           $("#prev-step").hide();

   }
   active_step(0);

   $("#next-step").click(function(){active('next')});
   $("#prev-step").click(function(){active('prev')});
       
   function active(type){
       var actif = $(".get-started-step").index($(".get-started-step:visible"));
       
       if(type=='next'){
           var go_to = actif+1;
       }else{
           var go_to = actif-1;
       }
       
       active_step(go_to);
   }

   $("#table-of-contents h2").click(function(){
       var go_to = $("#table-of-contents h2").index(this);
       active_step(go_to+1);
   })

   $("#to-table-of-contents").click(function(){
       active_step(0);
   })
});