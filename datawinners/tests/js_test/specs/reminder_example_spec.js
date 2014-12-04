describe("Calculation for next deadline for reminders", function() {

    it("should update example for next deadline in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,11,11).getTime());
        var monthly_reminder = new MonthlyReminder();
        monthly_reminder.calculate_deadline(11);
        expect(monthly_reminder.get_display_string()).toEqual("11 January 2015");

    });

    it("should update example for next deadline(february) in reminder settings", function () {
        sinon.useFakeTimers(new Date(2014,1,12).getTime());
        var monthly_reminder = new MonthlyReminder();
        monthly_reminder.calculate_deadline(30);
        expect(monthly_reminder.get_display_string()).toEqual("28 February 2014");
    });

    it("should update example for next deadline(lastday) in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,0,12).getTime());
        var monthly_reminder = new MonthlyReminder();
        monthly_reminder.calculate_deadline(0);
        expect(monthly_reminder.get_display_string()).toEqual("31 January 2014");
    });

    it("should update example for next deadline(lastday + january) in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,0,31).getTime());
        var monthly_reminder = new MonthlyReminder();
        var expected_date = new Date(2014,1,28);
        monthly_reminder.calculate_deadline(0);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
        expect(monthly_reminder.get_display_string()).toEqual("28 February 2014");
    });

    it("should update example for next deadline(lastday + february) in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,1,14).getTime());
        var monthly_reminder = new MonthlyReminder();
        var expected_date = new Date(2014,1,28);
        monthly_reminder.calculate_deadline(0);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
        expect(monthly_reminder.get_display_string()).toEqual("28 February 2014");
    });

    it("should update example for next deadline in reminder settings week", function () {
        sinon.useFakeTimers(new Date(2015,0,12).getTime());
        var weekly_reminder = new WeeklyReminder();
        expected_date = new Date(2015,0,15);
        weekly_reminder.calculate_deadline(4);
        expect(weekly_reminder.get_display_string()).toEqual("Thursday, 15 January 2015");
    });

    it("should update example for next deadline in reminder settings week", function () {
        var weekly_reminder = new WeeklyReminder();
        sinon.useFakeTimers(new Date(2015,0,1).getTime());
        expected_date = new Date(2015,0,8);
        weekly_reminder.calculate_deadline(4);
        expect(weekly_reminder.get_display_string()).toEqual("Thursday, 8 January 2015");
    });

    it("should throw an error when reminder message is empty ", function () {
        var reminder = new ReminderInstance();
        reminder.text("");
        reminder.enable(true);

        expect(reminder.is_valid()).toEqual(false);
    });

    it("should update the example for date greater than the current date to current month", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());
        var monthly_reminder = new MonthlyReminder();
        var reminder_view_model = new ReminderSettingsModel();
        expected_date = new Date(2014,11,7);
        monthly_reminder.calculate_deadline(7);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
        expect(monthly_reminder.get_display_string()).toEqual("7 December 2014");
    });

    it("should update the example for date lesser than the current date to next month", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());
        var monthly_reminder = new MonthlyReminder();
        var reminder_view_model = new ReminderSettingsModel();
        expected_date = new Date(2015,0,2);
        monthly_reminder.calculate_deadline(2);
        expect(monthly_reminder.get_display_string()).toEqual("2 January 2015");
    });

    it("should update the example for day greater than the current day to current week", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());
        var weekly_reminder = new WeeklyReminder();
        var reminder_view_model = new ReminderSettingsModel();
        expected_date = new Date(2015,11,6);
        weekly_reminder.calculate_deadline(6);
        expect(weekly_reminder.get_display_string()).toEqual("Saturday, 6 December 2014");
    });

    it("should update the example for day lesser than the current day to next week", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());
        var weekly_reminder = new WeeklyReminder();
        expected_date = new Date(2015,11,9);
        weekly_reminder.calculate_deadline(2);
        expect(weekly_reminder.get_display_string()).toEqual("Tuesday, 9 December 2014");
    });

    it("should update the next deadline example when month is changed to week", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());
        var reminder_view_model = new ReminderSettingsModel();

        reminder_view_model.selected_frequency('month') ;
        reminder_view_model.select_day(6);
        expected_date_for_month = new Date(2014,11,6);
        expect(reminder_view_model.next_deadline_date().reminder_date).toEqual(expected_date_for_month);
        expect(reminder_view_model.next_deadline_string()).toEqual("Next deadline: 6 December 2014");

        reminder_view_model.selected_frequency('week');
        reminder_view_model.select_day(5);
        expected_date_for_week = new Date(2014,11,5);
        expect(reminder_view_model.next_deadline_date().reminder_date).toEqual(expected_date_for_week);
        expect(reminder_view_model.next_deadline_string()).toEqual("Next deadline: Friday, 5 December 2014");
    });

    it("should update the next deadline example when week is changed to month", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());
        var reminder_view_model = new ReminderSettingsModel();

        reminder_view_model.selected_frequency('week') ;
        reminder_view_model.select_day(5);
        expected_date_for_month = new Date(2014,11,5);
        expect(reminder_view_model.next_deadline_date().reminder_date).toEqual(expected_date_for_month);
        expect(reminder_view_model.next_deadline_string()).toEqual("Next deadline: Friday, 5 December 2014");

        reminder_view_model.selected_frequency('month');
        reminder_view_model.select_day(5);
        expected_date_for_week = new Date(2014,11,5);
        expect(reminder_view_model.next_deadline_date().reminder_date).toEqual(expected_date_for_week);
        expect(reminder_view_model.next_deadline_string()).toEqual("Next deadline: 5 December 2014");
    });


    it("should update the before deadline example when month is selected", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());

        var reminder_view_model = new ReminderSettingsModel();

        var reminderBeforeDeadlineMonth = reminder_view_model.reminder_before_deadline;
        reminderBeforeDeadlineMonth.multiplier = -1;
        reminder_view_model.selected_frequency('month');
        reminder_view_model.select_day(5);
        reminderBeforeDeadlineMonth.enable(true);
        reminderBeforeDeadlineMonth.number_of_days(7);

        expect(reminder_view_model.next_deadline_string()).toEqual("Next deadline: 5 December 2014");
        expect(reminder_view_model.reminder_before_deadline.next_date_as_string()).toEqual("Next scheduled Reminder: 29 December 2014");

    });

    it("should update the before deadline example when month is selected", function () {
        sinon.useFakeTimers(new Date(2014,11,4).getTime());

        var reminder_view_model = new ReminderSettingsModel();

        var reminderBeforeDeadline = reminder_view_model.reminder_before_deadline;
        reminderBeforeDeadline.multiplier = -1;
        reminder_view_model.selected_frequency('week');
        reminder_view_model.select_day(5);
        reminderBeforeDeadline.enable(true);
        reminderBeforeDeadline.number_of_days(3);

        expect(reminder_view_model.next_deadline_string()).toEqual("Next deadline: Friday, 5 December 2014");
        expect(reminder_view_model.reminder_before_deadline.next_date_as_string()).toEqual("Next scheduled Reminder: Tuesday, 9 December 2014");

    });
});

