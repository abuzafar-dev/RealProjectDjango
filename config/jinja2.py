from django.contrib import messages
from django.template.defaultfilters import date, linebreaks, truncatewords
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import template_localtime
from jinja2 import Environment


def date_filter(value, fmt):
    return date(template_localtime(value), fmt)


def initials(user):
    name = (user.get_full_name() or user.username or '?').strip()
    return ''.join(part[0] for part in name.split()[:2]).upper()


def display_name(user):
    return user.get_full_name() or user.username


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'get_messages': messages.get_messages,
        'now': timezone.now,
    })
    env.filters.update({
        'date': date_filter,
        'linebreaks': linebreaks,
        'truncatewords': truncatewords,
        'initials': initials,
        'display_name': display_name,
    })
    return env
