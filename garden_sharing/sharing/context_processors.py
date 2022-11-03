from .models import Warehouse


def post_form(request):
    return {
        'cities': Warehouse.objects.values('city').distinct()
    }
