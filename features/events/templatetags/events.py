import calendar as python_calendar
import datetime
from django import template
from django.core import urlresolvers
import itertools

register = template.Library()


class Calendar(python_calendar.LocaleHTMLCalendar):
    def __init__(self, events, firstweekday=0, locale=None):
        super().__init__(firstweekday, locale)
        self.today = datetime.date.today()
        self.events = {}
        for date, events in itertools.groupby(events, key=lambda e: e.date()):
            self.events[date] = list(events)

    def formatday(self, thedate, themonth):
        events = self.events.get(thedate, [])
        url = ''
        if len(events) == 1:
            url = events[0].get_absolute_url()
        elif len(events) > 1:
            url = urlresolvers.reverse(
                    'event-day', args=['{{:%{}}}'.format(c).format(thedate) for c in 'Ybd'])
        return {
                'day': thedate.day,
                'events': events,
                'in_month': thedate.month == themonth,
                'today': thedate == self.today,
                'url': url,
                }

    def formatmonthname(self, theyear, themonth):
        with python_calendar.different_locale(self.locale):
            return '%s %s' % (python_calendar.month_name[themonth], theyear)

    def formatmonthweeks(self, theyear, themonth):
        return [self.formatweek(week, themonth)
                for week in self.monthdatescalendar(theyear, themonth)]

    def formatweek(self, theweek, themonth):
        return [self.formatday(d, themonth) for d in theweek]

    def formatweekday(self, day):
        with python_calendar.different_locale(self.locale):
            return python_calendar.day_abbr[day]

    def formatweekheader(self):
        return [self.formatweekday(i) for i in self.iterweekdays()]


@register.inclusion_tag('calendar/_calendar.html', takes_context=True)
def calendar(context, events, size='preview'):
    c = Calendar(events)
    return {
            'size': size,
            'days': c.formatweekheader(),
            'group': context.get('group'),
            'month': c.formatmonthname(c.today.year, c.today.month),
            'weeks': c.formatmonthweeks(c.today.year, c.today.month),
            }


@register.filter
def upcoming_events(events, preview_length):
    return events.upcoming(preview_length)