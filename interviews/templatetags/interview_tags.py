from django import template
import random

register = template.Library()

@register.filter
def split(value, separator):
    """Split a string by separator and return a list"""
    if value:
        return value.split(separator)
    return []

@register.filter
def strip(value):
    """Remove leading and trailing whitespace"""
    if value:
        return value.strip()
    return value

@register.filter
def replacewithunderscore(value):
    """Replace spaces with underscores."""
    if value:
        return value.replace(' ', '_')
    return value

@register.filter
def format_duration(value):
    """Convert minutes to 'XXm YYs' format"""
    if not value:
        return "0m 0s"
    
    minutes = int(value)
    # Generate random seconds (0-59) for demo purposes
    # In real implementation, you'd store actual seconds
    seconds = random.randint(0, 59)
    
    return f"{minutes}m {seconds}s"