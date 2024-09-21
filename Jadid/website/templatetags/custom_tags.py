from django import template
from django.contrib.auth.decorators import login_required

register = template.Library()

@register.simple_tag(takes_context=True)
def include_if(context, a, b, template_name):
    """
    Custom template tag to include a template if a condition a==b is met.
    Usage: {% include_if a b 'template_name.html' %}
    """
    if a == b:
        return template.loader.render_to_string(template_name, context.flatten())
    return ''

@login_required()
@register.simple_tag(takes_context=True)
def render_if_user_is_authenticated(context, *args):
    target, request, user, template_name = args
    if target in request.session.get('groups', '').split(','):
        if user:
            return template.loader.render_to_string(template_name, context.flatten())
    return ''