from timesheet import TimeSheet
from datetime import timedelta
from collections import defaultdict


class Weekday:

    def __init__(self, data):
        self.data = data

    @staticmethod
    def duty_beyond_twelve_hours(shift):
        twelve_hours_duty = TimeSheet.get_shift_start(shift) + timedelta(hours=12)
        break_start = TimeSheet.get_break_start(shift)
        break_end = TimeSheet.get_break_end(shift)

        # break STARTS and ENDS AFTER 12hrs duty
        if break_start and break_end > twelve_hours_duty:
            duty_beyond_twelve_hours = (TimeSheet.get_shift_length(shift) - timedelta(hours=12)) - \
                                       TimeSheet.get_break_duration(shift)
            return duty_beyond_twelve_hours

        # break STARTS BEFORE and ENDS AFTER 12hrs duty
        elif break_start < twelve_hours_duty < break_end:
            duty_beyond_twelve_hours = TimeSheet.get_break_end(shift) - \
                                       (TimeSheet.get_shift_start(shift) + timedelta(hours=12))
            return duty_beyond_twelve_hours

        else:   # no break spanning AFTER 12hrs
            duty_beyond_twelve_hours = TimeSheet.get_shift_length(shift) - timedelta(hours=12)
            return duty_beyond_twelve_hours

    @staticmethod
    def duty_beyond_nine_hours(shift):
        twelve_hours_duty = TimeSheet.get_shift_start(shift) + timedelta(hours=12)
        nine_hours_duty = TimeSheet.get_shift_start(shift) + timedelta(hours=9)
        break_start = TimeSheet.get_break_start(shift)
        break_end = TimeSheet.get_break_end(shift)

        # break STARTS and ENDS AFTER 9hrs and BEFORE 12hrs
        if (break_start > nine_hours_duty and break_end > nine_hours_duty) and break_end < twelve_hours_duty:
            duty_beyond_nine_hours = TimeSheet.get_break_end(shift) - nine_hours_duty
            return duty_beyond_nine_hours

        # break STARTS AFTER 9hrs and ENDS AFTER 12hrs
        elif break_start > nine_hours_duty and break_end > twelve_hours_duty:
            duty_beyond_nine_hours = TimeSheet.get_break_start(shift) - nine_hours_duty
            return duty_beyond_nine_hours

        # break STARTS BEFORE 9hrs and ENDS AFTER 9hrs duty
        elif break_start < nine_hours_duty < break_end < twelve_hours_duty:
            duty_beyond_nine_hours = TimeSheet.get_break_end(shift) - nine_hours_duty
            return duty_beyond_nine_hours

        else:   # if no break between 9hrs and 12hrs duty, use the full 3hrs
            duty_beyond_nine_hours = timedelta(hours=3)
            return duty_beyond_nine_hours

    @staticmethod
    def hours_after_six_and_less_than_nine(shift):
        six_pm = TimeSheet.get_shift_end(shift).replace(hour=18, minute=0)
        duty_beyond_twelve = Weekday.duty_beyond_twelve_hours(shift)
        duty_beyond_nine = Weekday.duty_beyond_nine_hours(shift)
        overtime_duty = duty_beyond_twelve + duty_beyond_nine
        duty_remainder = TimeSheet.get_shift_length(shift) - overtime_duty
        start_plus_remainder = TimeSheet.get_shift_start(shift) + duty_remainder
        break_start = TimeSheet.get_break_start(shift)
        break_end = TimeSheet.get_break_end(shift)

        if TimeSheet.get_shift_start(shift) + duty_remainder > six_pm:
            if break_start and break_end < six_pm:  # break STARTS and ENDS BEFORE 6pm
                hours_after_six_pm = (start_plus_remainder - six_pm) - TimeSheet.get_break_duration(shift)
                return hours_after_six_pm

            elif break_start < six_pm < break_end:  # break STARTS BEFORE and ENDS AFTER 6pm
                break_after_six_pm = TimeSheet.get_break_end(shift) - six_pm
                hours_after_six_pm = (start_plus_remainder - six_pm) - break_after_six_pm
                return hours_after_six_pm

            else:   # no break spanning AFTER 6pm
                hours_after_six_pm = timedelta(hours=0, minutes=0)
                return hours_after_six_pm

        else:   # no break within the reminder of duty up to 9hrs
            hours_after_six_pm = timedelta(hours=0, minutes=0)
            return hours_after_six_pm

    @staticmethod
    def hours_before_six_and_less_than_nine(shift):
        six_pm = TimeSheet.get_shift_end(shift).replace(hour=18, minute=0)
        break_start = TimeSheet.get_break_start(shift)
        break_end = TimeSheet.get_break_end(shift)

        # shifts where 6pm comes BEFORE 9 hours duty
        if (TimeSheet.get_shift_start(shift) + timedelta(hours=9)) > TimeSheet.get_shift_end(shift) \
                .replace(hour=18, minute=0) < TimeSheet.get_shift_end(shift).replace(hour=12, minute=0):
            if break_start and break_end < six_pm:  # break STARTS and ENDS BEFORE 6pm
                hours_before_six_pm = (TimeSheet.get_shift_start(shift) + six_pm) - TimeSheet.get_break_duration(shift)
                return hours_before_six_pm

            elif break_start < six_pm < break_end:  # break STARTS BEFORE and ENDS AFTER 6pm
                break_before_six_pm = six_pm - TimeSheet.get_break_start(shift)
                hours_before_six_pm = (six_pm - TimeSheet.get_shift_start(shift)) - break_before_six_pm
                return hours_before_six_pm

            else:   # no break spanning BEFORE 6pm
                hours_before_six_pm = TimeSheet.get_shift_end(shift).replace(hour=18, minute=0) - \
                                      TimeSheet.get_shift_start(shift)
                return hours_before_six_pm

        else:   # no break BEFORE 6pm up to 9hrs
            hours_before_six_pm = TimeSheet.get_shift_end(shift).replace(hour=18, minute=0) - \
                                  TimeSheet.get_shift_start(shift)
            return hours_before_six_pm

    @staticmethod
    def pay_beyond_twelve(hours, wage_rate):
        return (hours * wage_rate) * 2.25

    @staticmethod
    def pay_beyond_nine(hours, wage_rate):
        return (hours * wage_rate) * 1.75

    @staticmethod
    def pay_after_six_pm(hours, wage_rate):
        return (hours * wage_rate) * 1.30

    @staticmethod
    def pay_before_six_pm(hours, wage_rate):
        return (hours * wage_rate) * 1.25

    def get_weekday_pay(self):
        payslip = defaultdict(float)
        wage_rate = 0

        for shift in self.data['shifts']:

            if TimeSheet.get_shift_start(shift).isoweekday() < 6:  # day of week before saturday
                wage_level = float(shift['wageLevel'])  # get wage level for shift
                if wage_level == 1:
                    wage_rate = float(self.data['wageLevels']['1'])
                elif wage_level == 2:
                    pass
                elif wage_level == 3:
                    wage_rate = float(self.data['wageLevels']['3'])

                shift_length = TimeSheet.get_shift_length(shift)

                if shift_length > timedelta(hours=12):  # shift lengths greater than 12hrs
                    if shift.get('breakStart'):     # has a break

                        # pay over 12hrs duty
                        pay_beyond_twelve_hours = \
                            round(Weekday.pay_beyond_twelve(Weekday.duty_beyond_twelve_hours(shift).total_seconds()
                                                            / 3600, wage_rate), 3)
                        if 'pay_beyond_twelve_hours' in payslip:
                            payslip['pay_beyond_twelve_hours'] += pay_beyond_twelve_hours
                            payslip['duty_beyond_twelve_hours'] += \
                                Weekday.duty_beyond_twelve_hours(shift).total_seconds() / 3600
                        else:
                            payslip['pay_beyond_twelve_hours'] = pay_beyond_twelve_hours
                            payslip['duty_beyond_twelve_hours'] = \
                                Weekday.duty_beyond_twelve_hours(shift).total_seconds() / 3600

                        # pay over 9hrs but less than 12hrs duty
                        pay_beyond_nine_hours = \
                            round(Weekday.pay_beyond_nine(Weekday.duty_beyond_nine_hours(shift).total_seconds()
                                                          / 3600, wage_rate), 3)
                        if 'pay_beyond_nine_hours' in payslip:
                            payslip['pay_beyond_nine_hours'] += pay_beyond_nine_hours
                            payslip['duty_beyond_nine_hours'] += \
                                Weekday.duty_beyond_nine_hours(shift).total_seconds() / 3600
                        else:
                            payslip['pay_beyond_nine_hours'] = pay_beyond_nine_hours
                            payslip['pay_beyond_nine_hours'] = \
                                Weekday.duty_beyond_nine_hours(shift).total_seconds() / 3600

                        # pay less than 9hrs duty but BEFORE 6pm
                        pay_beyond_six_pm = \
                            round(Weekday.pay_after_six_pm(Weekday.hours_after_six_and_less_than_nine(shift)
                                                           .total_seconds() / 3600, wage_rate), 3)
                        if 'pay_after_six_pm' in payslip:
                            payslip['pay_after_six_pm'] += pay_beyond_six_pm
                            payslip['duty_after_six_pm'] += \
                                Weekday.hours_after_six_and_less_than_nine(shift).total_seconds() / 3600
                        else:
                            payslip['pay_after_six_pm'] = pay_beyond_six_pm
                            payslip['duty_after_six_pm'] = \
                                Weekday.hours_after_six_and_less_than_nine(shift).total_seconds() / 3600

                        # pay less than 9hrs duty but BEFORE 6pm
                        pay_before_six_pm = \
                            round(Weekday.pay_before_six_pm(Weekday.hours_before_six_and_less_than_nine(shift)
                                                            .total_seconds() / 3600, wage_rate), 3)
                        if 'pay_before_six_pm' in payslip:
                            payslip['pay_before_six_pm'] += pay_before_six_pm
                            payslip['duty_before_six_pm'] += \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() / 3600
                        else:
                            payslip['pay_before_six_pm'] = pay_before_six_pm
                            payslip['duty_before_six_pm'] = \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() /3600

                if timedelta(hours=9) < shift_length < timedelta(hours=12):  # duty over 9hrs and less than 12hrs
                    if shift.get('breakStart'):     # has a break

                        # pay over 9hrs but less than 12hrs duty
                        pay_beyond_nine_hours = \
                            round(Weekday.pay_beyond_nine(Weekday.duty_beyond_nine_hours(shift).total_seconds()
                                                          / 3600, wage_rate), 3)
                        if 'pay_beyond_nine_hours' in payslip:
                            payslip['pay_beyond_nine_hours'] += pay_beyond_nine_hours
                            payslip['duty_beyond_nine_hours'] += \
                                Weekday.duty_beyond_nine_hours(shift).total_seconds() / 3600
                        else:
                            payslip['pay_beyond_nine_hours'] = pay_beyond_nine_hours
                            payslip['duty_beyond_nine_hours'] = \
                                Weekday.duty_beyond_nine_hours(shift).total_seconds() / 3600

                        # pay less than 9hrs duty but BEFORE 6pm
                        pay_beyond_six_pm = \
                            round(Weekday.pay_after_six_pm(Weekday.hours_after_six_and_less_than_nine(shift)
                                                           .total_seconds() / 3600, wage_rate), 3)
                        if 'pay_after_six_pm' in payslip:
                            payslip['pay_after_six_pm'] += pay_beyond_six_pm
                            payslip['duty_after_six_pm'] += \
                                Weekday.hours_after_six_and_less_than_nine(shift).total_seconds() / 3600
                        else:
                            payslip['pay_after_six_pm'] = pay_beyond_six_pm
                            payslip['duty_after_six_pm'] = \
                                Weekday.hours_after_six_and_less_than_nine(shift).total_seconds() / 3600

                        # pay less than 9hrs duty but BEFORE 6pm
                        pay_before_six_pm = \
                            round(Weekday.pay_before_six_pm(Weekday.hours_before_six_and_less_than_nine(shift)
                                                            .total_seconds() / 3600, wage_rate), 3)
                        if 'pay_before_six_pm' in payslip:
                            payslip['pay_before_six_pm'] += pay_before_six_pm
                            payslip['duty_before_six_pm'] += \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() / 3600
                        else:
                            payslip['pay_before_six_pm'] = pay_before_six_pm
                            payslip['duty_before_six_pm'] = \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() / 3600

                    else:   # has no break
                        pay_beyond_nine_hours = round(Weekday.pay_beyond_nine(3.0, wage_rate), 3)

                        if 'pay_beyond_nine_hours' in payslip:
                            payslip['pay_beyond_nine_hours'] += pay_beyond_nine_hours
                            payslip['duty_beyond_nine_hours'] += 3.0
                        else:
                            payslip['pay_beyond_nine_hours'] = pay_beyond_nine_hours
                            payslip['duty_beyond_nine_hours'] = 3.0

                elif shift_length < timedelta(hours=9):     # duty less than 9hrs
                    if shift.get('breakStart'):     # has a break

                        # pay less than 9hrs duty but BEFORE 6pm
                        pay_beyond_six_pm = \
                            round(Weekday.pay_after_six_pm(Weekday.hours_after_six_and_less_than_nine(shift)
                                                           .total_seconds() / 3600, wage_rate), 3)
                        if 'pay_after_six_pm' in payslip:
                            payslip['pay_after_six_pm'] += pay_beyond_six_pm
                            payslip['duty_after_six_pm'] += \
                                Weekday.hours_after_six_and_less_than_nine(shift).total_seconds() / 3600
                        else:
                            payslip['pay_after_six_pm'] = pay_beyond_six_pm
                            payslip['duty_after_six_pm'] = \
                                Weekday.hours_after_six_and_less_than_nine(shift).total_seconds() / 3600

                        # pay less than 9hrs duty but BEFORE 6pm
                        pay_before_six_pm = \
                            round(Weekday.pay_before_six_pm(Weekday.hours_before_six_and_less_than_nine(shift)
                                                            .total_seconds() / 3600, wage_rate), 3)
                        if 'pay_before_six_pm' in payslip:
                            payslip['pay_before_six_pm'] += pay_before_six_pm
                            payslip['duty_before_six_pm'] += \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() / 3600
                        else:
                            payslip['pay_before_six_pm'] = pay_before_six_pm
                            payslip['duty_before_six_pm'] = \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() / 3600

                    else:   # has no break
                        pay_before_six_pm = \
                            round(Weekday.pay_before_six_pm(Weekday.hours_before_six_and_less_than_nine(shift)
                                                            .total_seconds() / 3600, wage_rate), 3)
                        if 'pay_before_six_pm' in payslip:
                            payslip['pay_before_six_pm'] += pay_before_six_pm
                            payslip['duty_before_six_pm'] += \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() / 3600
                        else:
                            payslip['pay_before_six_pm'] = pay_before_six_pm
                            payslip['duty_before_six_pm'] = \
                                Weekday.hours_before_six_and_less_than_nine(shift).total_seconds() / 3600
        return payslip
