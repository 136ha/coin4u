from datetime import datetime, date, timedelta

from django.utils.safestring import mark_safe
from django.views.generic import ListView

from calendarapp.models import Event
from calendarapp.utils import Calendar

import calendar

# https://velog.io/@2hey9/Project-%ED%94%8C%EB%A0%88%EC%9D%B4%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%9E%A5%EA%B3%A0-%EB%AF%B8%EB%8B%88%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EC%BA%98%EB%A6%B0%EB%8D%94-%EC%95%B1-%EA%B5%AC%EB%8F%99%ED%95%98%EA%B8%B0

class CalendarView(ListView):
    model = Event
    template_name = 'calendarapp/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)

        # Get previous and next month
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        return context

def get_date(req_day):
    try:
        if req_day:
            year, month, day = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
    except (ValueError, TypeError):
        pass
    return datetime.today().date()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    a = 'day=' + str(prev_month.year) + '-' + str(prev_month.month) + '-' + str(prev_month.day)
    return a


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    a = 'day=' + str(next_month.year) + '-' + str(next_month.month) + '-' + str(next_month.day)
    return a

