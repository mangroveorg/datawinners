
var CalculateDays = function(to_date, from_date) {
    var self = this;
    this.to_date = to_date;
    this.from_date = from_date;
    this.month_name_map = {
        0: gettext('January'),
        1: gettext('February'),
        2: gettext('March'),
        3: gettext('April'),
        4: gettext('May'),
        5: gettext('June'),
        6: gettext('July'),
        7: gettext('August'),
        8: gettext('September'),
        9: gettext('October'),
        10: gettext('November'),
        11: gettext('December')
    };

    this.get_difference_between_dates = function(){
        return (self.to_date.getDate() - self.from_date.getDate());
    };

    this.get_formatted_date_for_poll = function(date){
        return  date.getDate() +" " + this.month_name_map[date.getMonth()] +" "+ date.getFullYear();
    };

};
