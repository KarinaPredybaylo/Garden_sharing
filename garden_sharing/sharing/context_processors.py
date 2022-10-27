from django.db.models import F

from .forms import WarehouseForm
from .models import Warehouse


def post_form(request):
    return {
        # 'city_form': WarehouseForm(data={'warehouse_id': request.session.get('warehouse_id', None)}),
        'cities': Warehouse.objects.values('city').distinct()
    }
