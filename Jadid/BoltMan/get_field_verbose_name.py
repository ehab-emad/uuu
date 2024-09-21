from django.template import Library

register = Library()


@register.simple_tag
def get_field_verbose_name(instance, field_name):
    """Returns the verbose_name of the specified field."""
    return instance._meta.get_field(field_name).verbose_name.title()