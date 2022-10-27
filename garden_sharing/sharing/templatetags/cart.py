from django import template

register = template.Library()


@register.filter(name='in_cart')
def in_cart(thing, cart):
    keys = cart.keys()
    for k in keys:
        if int(k) == thing.id:
            return True
    return False


@register.filter(name='cart_quantity')
def cart_quantity(thing, cart):
    keys = cart.keys()
    for obj in keys:
        if int(obj) == thing.id:
            return cart.get(id)
    return 0
