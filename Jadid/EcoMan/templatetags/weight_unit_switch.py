from django import template

register = template.Library()

@register.filter(name='to_grams')
def to_grams(value, arg = 1000):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
@register.simple_tag
def weight_conversion(value, target_unit='KILOGRAMS', decimal_places=3):
    try:
        if decimal_places< 0:
            decimal_places = 3
        value = float(value)
        
        if target_unit.upper() == 'GRAMS':
            result = value *1000  # No conversion needed, it's already in grams
            unit = '[g]'
        elif target_unit.upper() == 'KILOGRAMS':
            result = value  # Convert grams to kilograms
            unit = '[kg]'
        else:
            return ''  # Return an empty string for unsupported units
        
        # Round the result to the specified number of decimal places
        rounded_result = round(result, int(decimal_places))
        
        # Return the result as a string with the unit in hard brackets
        return f"{rounded_result:.{decimal_places}f} {unit}"
    except (ValueError, TypeError):
        return ''  # Return an empty string in case of conversion error
@register.simple_tag
def weight_conversion_no_unit(value, target_unit='KILOGRAMS', decimal_places=3):
    try:
        if decimal_places< 0:
            decimal_places = 3
        value = float(value)
        
        if target_unit.upper() == 'GRAMS':
            result = value *1000  # No conversion needed, it's already in grams
        elif target_unit.upper() == 'KILOGRAMS':
            result = value  # Convert grams to kilograms
        else:
            return ''  # Return an empty string for unsupported units
        
        # Round the result to the specified number of decimal places
        rounded_result = round(result, int(decimal_places))
        
        # Return the result as a string with the unit in hard brackets
        return f"{rounded_result:.{decimal_places}f}"
    except (ValueError, TypeError):
        return ''  # Return an empty string in case of conversion error
        

@register.simple_tag
def weight_unit(value):
    try:

        if value.upper() == 'GRAMS':
            unit = '[g]'
        elif value.upper() == 'KILOGRAMS':
            unit = '[kg]'
        else:
            return ''  # Return an empty string for unsupported units
        
        # Return the result as a string with the unit in hard brackets
        return f" {unit}"
    except (ValueError, TypeError):
        return ''  # Return an empty string in case of conversion error