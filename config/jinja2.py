from django.contrib import messages
from django.template.defaultfilters import date, linebreaks, truncatewords
from django.templatetags.static import static
from django.urls import reverse
from django.utils.timezone import template_localtime
from jinja2 import Environment


def date_filter(value, fmt):
    return date(template_localtime(value), fmt)


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'get_messages': messages.get_messages,
    })
    env.filters.update({
        'date': date_filter,
        'linebreaks': linebreaks,
        'truncatewords': truncatewords,
    })
    return env
