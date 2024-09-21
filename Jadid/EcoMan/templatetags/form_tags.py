from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_field(field, css_class="form-control"):
    # Generate the HTML for the label, field, and errors
    label_html = field.label_tag(attrs={'class': 'control-label'})
    field_html = field.as_widget(attrs={'class': css_class})
    error_html = ''.join([f'<p class="help-block text-danger">{error}</p>' for error in field.errors])
    
    # Return the combined HTML
    return mark_safe(f'<div class="form-group{" has-error" if field.errors else ""}">'
                     f'{label_html}{field_html}{error_html}</div>')