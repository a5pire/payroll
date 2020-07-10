from datetime import datetime, timedelta


class TimeSheet:

    def __init__(self, data):
        self.data = data

    @staticmethod
    def get_wage_level(shift):
        wage_level = shift['wageLevel']
        for _ in shift:
            return wage_level

    @staticmethod
    def get_shift_start(shift):
        start = shift['start']
        return datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def get_shift_end(shift):
        end = shift['end']
        return datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def get_shift_length(shift):
        return TimeSheet.get_shift_end(shift) - TimeSheet.get_shift_start(shift)

    @staticmethod
    def get_break_start(shift):
        if shift.get('breakStart'):
            start = shift['breakStart']
            return datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def get_break_duration(shift):
        if shift.get('breakDurationMinutes'):
            duration = int(shift['breakDurationMinutes'])
            break_duration = timedelta(minutes=duration)
        else:
            break_duration = timedelta(hours=0, minutes=0)
        return break_duration

    @staticmethod
    def get_break_end(shift):
        if shift.get('breakStart'):
            start = shift['breakStart']
            start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            return TimeSheet.get_break_start(shift) + TimeSheet.get_break_duration(shift)

    @staticmethod
    def weekdays(shift):
        day_of_week = shift['start']
        day_of_week_obj = datetime.strptime(day_of_week, '%Y-%m-%dT%H:%M:%S')
        return day_of_week_obj.isoweekday()

    @staticmethod
    def six_pm_shift_end(shift):
        six_pm = TimeSheet.get_shift_end(shift) - TimeSheet.get_shift_end(shift).replace(hour=18, minute=0)
        if six_pm is None:
            six_pm = timedelta(hours=0, minutes=0)
            return six_pm
        return six_pm

    @staticmethod
    def breaks_across_six_pm(shift):
        if shift.get('breakStart'):
            six_pm = TimeSheet.get_break_start(shift).replace(hour=18, minute=0)
            if (TimeSheet.get_shift_start(shift).isoweekday() != 6 or TimeSheet.get_shift_start(shift) != 7) and \
               TimeSheet.get_break_start(shift) < six_pm < TimeSheet.get_break_end(shift):
                break_after_six_pm = TimeSheet.get_break_end(shift) - six_pm
            else:
                break_after_six_pm = timedelta(hours=0, minutes=0)
        else:
            break_after_six_pm = timedelta(hours=0, minutes=0)

        return break_after_six_pm

    @staticmethod
    def get_normal_hours(shift):
        total_hours = 0.0

        if TimeSheet.get_shift_start(shift).isoweekday() < 6:  # before saturday
            if shift.get('breakStart'):

                # has a break: shift ends at or before 6pm: break within normal hours
                if TimeSheet.get_shift_end(shift) <= TimeSheet.get_shift_end(shift).replace(hour=18, minute=0):
                    normal_hours = TimeSheet.get_shift_length(shift) - TimeSheet.get_break_duration(shift)
                    if normal_hours is None:
                        normal_hours = timedelta(hours=0, minutes=0)
                        total_hours += normal_hours.total_seconds() / 3600
                    else:
                        total_hours += normal_hours.total_seconds() / 3600

                # has break: end of shift AFTER 6pm: break starts AFTER 6pm
                if (TimeSheet.get_shift_end(shift) > TimeSheet.get_shift_end(shift).replace(hour=18, minute=0)) and \
                   TimeSheet.get_break_start(shift) > TimeSheet.get_break_start(shift).replace(hour=18, minute=0):
                    normal_hours = TimeSheet.get_shift_end(shift).replace(hour=18, minute=0) - \
                                   TimeSheet.get_shift_start(shift)
                    if normal_hours is None:
                        normal_hours = timedelta(hours=0, minutes=0)
                        total_hours += normal_hours.total_seconds() / 3600
                    else:
                        total_hours += normal_hours.total_seconds() / 3600

                # has break: end of shift AFTER 6pm: break starts BEFORE 6pm and ends AFTER 6pm
                if TimeSheet.get_shift_end(shift) > TimeSheet.get_shift_end(shift).replace(hour=18, minute=0) and \
                   (TimeSheet.get_break_start(shift) < TimeSheet.get_shift_end(shift).replace(hour=18, minute=0)
                   < TimeSheet.get_break_end(shift)):
                    break_end = TimeSheet.get_break_end(shift)
                    break_after_six_pm = break_end - TimeSheet.get_break_end(shift).replace(hour=18, minute=0)
                    break_before_six_pm = TimeSheet.get_break_duration(shift) - break_after_six_pm
                    normal_hours = (TimeSheet.get_shift_end(shift).replace(hour=18, minute=0)
                                    - TimeSheet.get_shift_start(shift)) - break_before_six_pm
                    if normal_hours is None:
                        normal_hours = timedelta(hours=0, minutes=0)
                        total_hours += normal_hours.total_seconds() / 3600
                    else:
                        total_hours += normal_hours.total_seconds() / 3600

                # has break: end of shift AFTER 6pm: break starts BEFORE and ends BEFORE 6pm
                if TimeSheet.get_shift_end(shift) > TimeSheet.get_shift_end(shift).replace(hour=18, minute=0) and \
                   TimeSheet.get_break_end(shift) < TimeSheet.get_break_end(shift).replace(hour=18, minute=0):
                    normal_hours = TimeSheet.get_shift_end(shift).replace(hour=18, minute=0) - \
                                   TimeSheet.get_shift_start(shift) - TimeSheet.get_break_duration(shift)
                    if normal_hours is None:
                        normal_hours = timedelta(hours=0, minutes=0)
                        total_hours += normal_hours.total_seconds() / 3600
                    else:
                        total_hours += normal_hours.total_seconds() / 3600

            # no break: shift end BEFORE 6pm
            elif TimeSheet.get_shift_end(shift) <= TimeSheet.get_shift_end(shift).replace(hour=18, minute=0):
                normal_hours = TimeSheet.get_shift_end(shift) - TimeSheet.get_shift_start(shift)
                if normal_hours is None:
                    normal_hours = timedelta(hours=0, minutes=0)
                    total_hours += normal_hours.total_seconds() / 3600
                else:
                    total_hours += normal_hours.total_seconds() / 3600

            # no break: shift starts BEFORE 6pm and ends AFTER 6pm
            elif TimeSheet.get_shift_start(shift) < TimeSheet.get_shift_end(shift).replace(hour=18, minute=0) \
                    < TimeSheet.get_shift_end(shift):
                duration_after_six_pm = TimeSheet.get_shift_end(shift)\
                                                - TimeSheet.get_shift_end(shift).replace(hour=18, minute=0)
                normal_hours = TimeSheet.get_shift_length(shift) - duration_after_six_pm
                if normal_hours is None:
                    normal_hours = timedelta(hours=0, minutes=0)
                    total_hours += normal_hours.total_seconds() / 3600
                else:
                    total_hours += normal_hours.total_seconds() / 3600

        return total_hours
