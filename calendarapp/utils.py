import datetime
from calendar import HTMLCalendar
from calendarapp.models import Event
import pandas as pd
from colour import Color
import calendar
from indicatorapp.models import Ohlcv

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	def formatday(self, day, events, ohlcv):
		# get ohlcv data for color of the day
		ohlcv = ohlcv[(ohlcv['timestamp'].dt.year==self.year) & (ohlcv['timestamp'].dt.month==self.month)].copy()
		ohlcv['day'] = ohlcv['timestamp'].dt.day
		ohlcv.set_index('day', drop=True, inplace=True)
		ohlcv['volatility'] = ohlcv['Close'] - ohlcv['Open']

		# set color for each day
		color_red = []
		if len(ohlcv[ohlcv['volatility'] < 0]) != 0:
			color_red = list(Color("#D32F2F").range_to(Color("white"), len(ohlcv[ohlcv['volatility'] < 0])))
		color_green = []
		if len(ohlcv[ohlcv['volatility'] > 0]) != 0:
			color_green = list(Color("white").range_to(Color("#388E3C"), len(ohlcv[ohlcv['volatility'] > 0])))

		colors = color_red + color_green

		ohlcv.sort_values(by=['volatility'], axis=0, inplace=True)
		ohlcv['color'] = ['%s' % c for c in colors]

		# set HTML
		events_per_day = events.filter(date__day=day).order_by('-epsSurprisePct')
		d = ''
		if len(events_per_day) > 5:
			events_per_day = events_per_day[:5]
		for event in events_per_day:
			d += f'<li data-bs-toggle="tooltip" data-bs-placement="top" title="epsEstimate:{event.epsEstimate} | epsActual:{event.epsActual} | epsSurprisePct:{event.epsSurprisePct}"> {event.name} {event.epsEstimate - event.epsActual} </li>'
		if day != 0:
			if day in ohlcv.index:
				return f"<td bgcolor={ohlcv['color'][day]}><span class='date'>{day}</span><ul>{d}</ul></td>"
			else:
				return f"<td><span class='date'>{day}</span><ul>{d}</ul></td>"
		return '<td></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events, ohlcv):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events, ohlcv)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, ohlcv, withyear=True):
		events = Event.objects.filter(date__year=self.year, date__month=self.month)

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events, ohlcv)}\n'
		cal += '</table>'
		return cal