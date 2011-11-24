$(document).ready(function(){
    $("form#contact_us").validate({
            rules: {
                category:{
                    required: true
                },
                email:{
                    required:true,
                    email: true
                },
                subject:{
                    required: true
                },
                message: {
                    required: true
                }
            },
            wrapper: "div",
            errorPlacement: function(error, element) {
                var offset = element.offset();
                error.insertAfter(element);
                error.addClass('error_arrow');  // add a class to the wrapper
            }
    });
});