from itertools import chain
from .models import *
# from django.contrib.sites.shortcuts import get_current_site
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site


def get_product(id):
    plants = Plant.objects.all()
    tools = Tool.objects.all()
    products = list(chain(plants, tools))
    product = [product for product in products if product.id == id]
    return product[0]


def get_domain(request):
    current_site = get_current_site(request)
    domain = current_site.domain
    return domain
