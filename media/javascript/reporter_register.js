$(document).ready(function(){
    $('#registration_form div.required label').each(function(){
        $('<span style="color:red">*</span>').insertAfter(this);
    });
    $('#flash-message').delay(10000).fadeOut();
});