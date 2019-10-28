from timesheet import TimeSheet
from datetime import timedelta
from collections import defaultdict


class Saturday:

    def __init__(self, data):
        self.data = data

    def get_saturday_pay(self):
        payslip = defaultdict(float)
        wage_rate = 0

        for shift in self.data['shifts']:
            day_of_week = TimeSheet.weekdays(shift)

            if day_of_week == 6:  # get hours for Saturday
                wage_level = float(shift['wageLevel'])  # get wage level for shift
                if wage_level == 1:
                    wage_rate = float(self.data['wageLevels']['1'])
                elif wage_level == 2:
                    pass
                elif wage_level == 3:
                    wage_rate = float(self.data['wageLevels']['3'])

                if shift.get('breakStart'):  # looks for shifts with a break
                    shift_length = TimeSheet.get_shift_length(shift)
                    break_duration = TimeSheet.get_break_duration(shift)
                    nett_hours = shift_length - break_duration

                    if nett_hours > timedelta(hours=12):  # shift length greater than 12hrs
                        plus_twelve_hours = nett_hours - timedelta(hours=12)
                        plus_twelve = (plus_twelve_hours.total_seconds() / 3600 * wage_rate) * 2.25
                        plus_nine_hours = 3.0
                        plus_nine = (plus_nine_hours * wage_rate) * 1.75
                        normal_hours = (9.0 * wage_rate) * 1.50

                        if 'saturday_plus_twelve' in payslip:
                            payslip['saturday_plus_twelve'] += round(plus_twelve, 3)
                        else:
                            payslip['saturday_plus_twelve'] = round(plus_twelve, 3)

                        if 'saturday_plus_nine' in payslip:
                            payslip['saturday_plus_nine'] += round(plus_nine, 3)
                        else:
                            payslip['saturday_plus_nine'] = round(plus_nine, 3)

                        if 'saturday_normal' in payslip:
                            payslip['saturday_normal'] += round(normal_hours, 3)
                        else:
                            payslip['saturday_normal'] = round(normal_hours, 3)

                    elif nett_hours > timedelta(hours=9) <= timedelta(hours=12):  # shift length 9-12hrs
                        plus_nine_hours = nett_hours - timedelta(hours=9)
                        plus_nine = (plus_nine_hours.total_seconds() / 3600 * wage_rate) * 1.75
                        normal_hours = (9.0 * wage_rate) * 1.50

                        if 'saturday_plus_nine' in payslip:
                            payslip['saturday_plus_nine'] += round(plus_nine, 3)
                        else:
                            payslip['saturday_plus_nine'] = round(plus_nine, 3)

                        if 'saturday_normal' in payslip:
                            payslip['saturday_normal'] += round(normal_hours, 3)
                        else:
                            payslip['saturday_normal'] = round(normal_hours, 3)

                    else:  # shift length less than 9hrs
                        normal_hours = (nett_hours.total_seconds() / 3600 * wage_rate) * 1.50

                        if 'saturday_normal' in payslip:
                            payslip['saturday_normal'] += round(normal_hours, 3)
                        else:
                            payslip['saturday_normal'] = round(normal_hours, 3)

                else:  # same logic as above with no break during the shift
                    shift_length = TimeSheet.get_shift_length(shift)

                    if shift_length > timedelta(hours=12):
                        plus_twelve_hours = shift_length - timedelta(hours=12)
                        plus_twelve = (plus_twelve_hours.total_seconds() / 3600 * wage_rate) * 2.25
                        plus_nine_hours = 3.0
                        plus_nine = (plus_nine_hours * wage_rate) * 1.75
                        normal_hours = (9.0 * wage_rate) * 1.50

                        if 'saturday_plus_twelve' in payslip:
                            payslip['saturday_plus_twelve'] += round(plus_twelve, 3)
                        else:
                            payslip['saturday_plus_twelve'] = round(plus_twelve, 3)

                        if 'saturday_plus_nine' in payslip:
                            payslip['saturday_plus_nine'] += round(plus_nine, 3)
                        else:
                            payslip['saturday_plus_nine'] = round(plus_nine, 3)

                        if 'saturday_normal' in payslip:
                            payslip['saturday_normal'] += round(normal_hours, 3)
                        else:
                            payslip['saturday_normal'] = round(normal_hours, 3)

                    elif shift_length > timedelta(hours=9) <= timedelta(hours=12):  # shift length 9-12hrs
                        plus_nine_hours = shift_length - timedelta(hours=9)
                        plus_nine = (plus_nine_hours.total_seconds() / 3600 * wage_rate) * 1.75
                        normal_hours = (9.0 * wage_rate) * 1.50

                        if 'saturday_plus_nine' in payslip:
                            payslip['saturday_plus_nine'] += round(plus_nine, 3)
                        else:
                            payslip['saturday_plus_nine'] = round(plus_nine, 3)

                        if 'saturday_normal' in payslip:
                            payslip['saturday_normal'] += round(normal_hours, 3)
                        else:
                            payslip['saturday_normal'] = round(normal_hours, 3)

                    else:
                        normal_hours = (shift_length.total_seconds() / 3600 * wage_rate) * 1.50

                        if 'saturday_normal' in payslip:
                            payslip['saturday_normal'] += round(normal_hours, 3)
                        else:
                            payslip['saturday_normal'] = round(normal_hours, 3)

        return payslip
