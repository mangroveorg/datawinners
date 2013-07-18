    $(document).ready(function() {
        $( ".support-acc" ).accordion({ collapsible: true, active: false, autoHeight: false });

        $(".block_support").bind("mouseover", function(){
           $(this).addClass("block_support_hover");
        });

        $(".block_support").bind("mouseout", function(){
           $(this).removeClass("block_support_hover");
        });

        $(".block_support_hover").live("click", function(){
            location.href = $(".read_more", $(this)).attr("href");
        });
    });