from django import template
from datetime import date

register = template.Library()

# SEE : http://www.pfinn.net/custom-django-filter-tutorial.html
# Returns a more "user-friendly" date for recent past/future dates (+/- 5 days range), else just the date
# NOTE: This is likely not timezone aware!
@register.filter(name='get_date_as_string')
def get_date_as_string(date):
	delta = date - date.today()
	delta_days = delta.days

	if delta_days == 0:
		return "Today!"
	elif delta_days < 1 and delta_days > -5:
		return "%s %s ago!" % (abs(delta_days),("day" if abs(delta_days) == 1 else "days"))
	elif delta_days == 1:
		return "Tomorrow"
	elif delta.days > 1 and delta.days < 5:
		return "In %s days" % delta.days
	else:
		return date

@register.filter(name='currency_icon')
def currency_icon(currency_string):
	if currency_string == 'USD':
		return '$'
	else:
		return currency_string

@register.filter(name='unit_price_formatting')
def unit_price_formatting(unit_type):
	if unit_type == 'each':
		return 'each'
	else:
		return ' / ' + unit_type

@register.filter(name='as_percentage_of')
def as_percentage_of(part, whole):
    try:
        return "%d%%" % (part / whole * 100)
    except:
        return "0%"