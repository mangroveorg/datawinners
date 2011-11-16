//All the deadline related drop-downs. They are very very very annoying.
DW.DeadlineDetails = function(){
    this.deadlineSection = 'frequency_values';
    this.deadlineEnabledControl = 'input[name=deadline_enabled]';
    this.frequencyPeriodControl = 'select[name=frequency_period]';
    this.deadlineTypeControl = 'select[name=deadline_type]'; //For the control which lets user select Same and Following. I wish i had a better name for this one.
    this.deadlineMonthControl = 'select[name=deadline_month]';
    this.deadlineWeekControl = 'select[name=deadline_week]'
};

DW.DeadlineDetails.prototype = {
    init: function(){
        var is_deadline_enabled = ($(this.deadlineEnabledControl).val() === "True");
        if(is_deadline_enabled){
            this.show();
        }else{
            this.hide();
        }
        return true; //It's a Best Practice to return either true or false when there are only side effects happening inside a method.
    },
    hide: function(){
        $(this.deadlineSection).hide();
    },
    show: function(context){
        var is_week = ($(self.frequencyPeriodControl).val() === "week");
        if(is_week){
            this.toggle_when_week_is_selected();
        }else{
            this.toggle_when_month_is_selected();
        }
        $(self.deadlineSection).show(); //Showing stuff after everything has been set, should make the user not see that we are changing values in browsers like IE6-7
    },
    disable: function(){

    },
    toggle_when_month_is_selected: function(){
        $(this.deadlineMonthControl).show();
        $(this.deadlineWeekControl).hide();
    },
    toggle_when_week_is_selected: function(){
        $(this.deadlineWeekControl).show();
        $(this.deadlineMonthControl).hide();
    }
};

$(document).ready(function() {
    var deadlineDetails = new DW.DeadlineDetails;
    deadlineDetails.init();
    $(deadlineDetails.deadlineEnabledControl).change(deadlineDetails.init);
    $(deadlineDetails.frequencyPeriodControl).change(deadlineDetails.show);
});
