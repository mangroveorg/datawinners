$(document).ready(function(){
   function active_step(number){
       $(".get-started-step").hide();
       $(".get-started-step").eq(number).show();
   }
   active_step(1);

   $("#next-step").click(function(){active('next')});
   $("#prev-step").click(function(){active('prev')});
       
   function active(type){
       var actif = $(".get-started-step").index($(".get-started-step:visible"));
       var length = $(".get-started-step").length;
       if(type=='next'){
           var go_to = actif+1;
           $("#prev-step").show();
       }else{
           var go_to = actif-1;
           $("#next-step").show();
       }
       
       if((( type == 'next') && (go_to >= length -1))||(!go_to)){
         $("#"+type+"-step").hide();
       }
       active_step(go_to);
   }
});