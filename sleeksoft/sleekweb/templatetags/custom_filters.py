from django import template

register = template.Library()


@register.filter
def equals(value, arg):
    """
    Custom filter to compare two values.
    Usage: {% if value|equals:'something' %}...{% endif %}
    This avoids the == operator that formatters may break.
    """
    return value == arg
