import calendar

class Calendar(calendar.Calendar):
    def __init__(self, year, month):
        super().__init__(firstweekday=6)
        self.year = year
        self.month = month
        self.day_names = ('일', '월', '화', '수', '목', '금', '토')
        self.months = ('1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월')

    def get_days(self):
        weeks = self.monthdays2calendar(self.year, self.month)
        days = []
        for week in weeks:
            for day, _ in week:
                days.append(day)
                # print(days)
        return days

    def get_month(self):
        # print(self.months[self.month - 1])
        return self.months[self.month - 1]

