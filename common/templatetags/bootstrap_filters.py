from django import template

register = template.Library()

@register.filter
def bootstrap_alert_tag(tag):
    return "danger" if tag == "error" else tag
