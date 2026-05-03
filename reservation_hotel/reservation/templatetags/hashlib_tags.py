import hashlib
from django import template

register = template.Library()


@register.filter
def resa_token(resa_pk, client_pk):
    """Generate a secure token for reservation access"""
    return hashlib.sha256(f"{resa_pk}-{client_pk}-SECRET".encode()).hexdigest()[:16]
