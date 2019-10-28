#!/usr/bin/env python3

import sys
from open_data import Open
from timesheet import TimeSheet
from weekday import Weekday
from saturday import Saturday
from sunday import Sunday
from collections import defaultdict, Counter
import json

totals = defaultdict(float)


def main():

    file_path = Open(sys.argv[1])
    employee_data = file_path.open_json_file()
    time_sheet = TimeSheet(employee_data)
    weekday = Weekday(employee_data)
    saturday = Saturday(employee_data)
    sunday = Sunday(employee_data)

    pays = Counter(weekday.get_weekday_pay()) + Counter(saturday.get_saturday_pay()) + \
        Counter(sunday.get_sunday_pay())

    deposit = 0
    for value in pays.values():
        deposit += value

    pays['total_pay'] = round(deposit, 3)

    with open('data.json', 'w') as file:
        json.dump(pays, file)


if __name__ == '__main__':
    main()
