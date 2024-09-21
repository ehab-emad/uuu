from django import template

register = template.Library()

@register.filter
def order_by_time(query:any = None):
    try:
        sorted = query.order_by('-created_at')
        return sorted
    except ValueError:
        return None
    