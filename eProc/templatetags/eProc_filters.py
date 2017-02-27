from django import template
from datetime import date
import json
from django.utils.safestring import mark_safe

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

@register.filter(name='get_class')
def get_class(value):
  return value.__class__.__name__
  
@register.filter(name='currency_icon')
def currency_icon(currency_string):
	if currency_string == 'USD':
		return '$'
	else:
		return currency_string

@register.filter(name='currency_formatting')
def currency_formatting(amount, currency):
	if currency == 'USD':
		return '$' + str(amount)
	else:
		return curreny + str(amount)

@register.filter(name='unit_type_formatting')
def unit_type_formatting(unit_type):
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


@register.filter(name='divide')
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None

# To pass a list of strings from Django to JS, need to encode data to JSON
# http://stackoverflow.com/questions/21150133/pass-a-list-of-string-from-django-to-javascript
@register.filter
def as_json(data):
    return mark_safe(json.dumps(data))