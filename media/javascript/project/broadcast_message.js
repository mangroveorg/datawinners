DW.broadcast_sms=function(){
    this.clearElementId='#clear_broadcast_sms_form';
    this.formElementId="#broadcast_sms_form";
    this.idToElement="#id_to";
    this.messageCountElement="#messageCount";
    this.smsContentElement="#sms_content";
    this.maxSMSChar=160;
    this.additional_column=new DW.additional_column();

};

DW.broadcast_sms.prototype={
    init:function(){
        this.createSMSContentValidationRule();
        this.createAdditionalTelephoneValidationRule();
        this.processAddtionalColumnValidation();
        this.setMessageCount();
    },

    createAdditionalTelephoneValidationRule:function(){
        this.additional_column.createAdditionalTelephoneValidationRule();
    },
    createSMSContentValidationRule:function(){
        var defaults = $(this.formElementId).validate({
            rules: {
                text:{
                    required:true
                }
            },
            wrapper: "div",
            errorPlacement: function(error, element) {
                error.insertAfter(element);
                error.addClass('error_arrow');  // add a class to the wrapper
            }
        });

    },

    processAddtionalColumnValidation:function(){
        if (this.isAdditionalSelected()) {
            this.additional_column.addRule();
        }
        else {
            this.additional_column.removeRule();
        }

    },

    isAdditionalSelected:function(){
        return $(this.idToElement).val() == "Additional";
    },
    setMessageCount:function(){
        $(this.messageCountElement).html(this.getSMSLength() + "/"+this.maxSMSChar);
    },
    getSMSLength:function(){
        return $(this.smsContentElement).val().length;
    },
    clearContent:function(){
        $(this.formElementId)[0].reset();
        this.setMessageCount();

    }

};


DW.additional_column=function(){
    this.additionalPeopleId="#additional_people_column";
    this.telephoneNumbersElementId='#id_others';
    this.telephone_number_rule="regexrule";
};

DW.additional_column.prototype={
    createAdditionalTelephoneValidationRule:function(){
        $.validator.addMethod(this.telephone_number_rule, function(value, element) {
            var text = $('#' + element.id).val();
            var re = new RegExp('^[0-9 ,]+$');
            var string_has_non_numeric_char = re.test(text);
            if (!string_has_non_numeric_char){
                return false;
            }
            var telephone_numbers = text.split(',');
            var each;
            for (each in telephone_numbers){
                if (telephone_numbers[each].length>10){
                    return false;
                }
            }
            return true;
        }, gettext("Only 10 digit letters are valid"));

    },

    addRule:function(){
        $(this.additionalPeopleId).removeClass('none');
        $(this.telephoneNumbersElementId).rules("add", this.telephone_number_rule);
        $(this.telephoneNumbersElementId).rules("add", "required");

    },
    removeRule:function(){
        $(this.additionalPeopleId).addClass('none');
        $(this.telephoneNumbersElementId).rules("remove", this.telephone_number_rule);
        $(this.telephoneNumbersElementId).rules("remove", "required");

    }

};

$(document).ready(function() {
    var broadcast_sms=new DW.broadcast_sms();
    broadcast_sms.init();

    $('#sms_content').keyup(function() {
        broadcast_sms.setMessageCount();
    });

    $('#id_to').change(function() {
        broadcast_sms.processAddtionalColumnValidation();
    });

    $('#clear_broadcast_sms_form').click(function() {
        broadcast_sms.clearContent();
    });
});