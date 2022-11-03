from itertools import chain
from json import dumps
from cart.cart import Cart
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, F
from django.forms import formset_factory, modelformset_factory
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import decorators
from django.views import generic
from .forms import SharePlantsForm, ShareToolForm, \
    ToolsFormSet, PlantsFormSet, RequestThingForm, RequestUpdateForm, RequestThingFormSet
from .models import Warehouse, Share, Plant, Tool, TypePlant, CarePlant, Request, RequestThing, ShareThing
from django.db import transaction
from .utils import get_product, get_domain
from .tasks import send_email_update
import registration.models
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page, cache_control

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def set_city_session(request):
    if request.session['city'] is None:
        request.session['city'] = request.POST['city']
    print(request.session['city'])
    return redirect(reverse('home'))


@transaction.atomic
@decorators.login_required
def share_detail(request):
    if request.POST.get('share_p') or request.POST.get('share_t'):
        share_abstract = Share.objects.create(plants_amount=request.POST.get('share_p'),
                                              thing_amount=request.POST.get('share_t'), user=request.user)
        plants_amount = int(share_abstract.plants_amount)
        thing_amount = int(share_abstract.thing_amount)
        SharingPlantFormSet = formset_factory(SharePlantsForm,
                                              extra=plants_amount)
        SharingToolFormSet = formset_factory(ShareToolForm,
                                             extra=thing_amount)
        formset_plant = SharingPlantFormSet(prefix='plants')
        formset_tool = SharingToolFormSet(prefix='tools')
        context = {
            'plant_form': formset_plant,
            'tool_form': formset_tool,
        }
        return render(request, 'share_detail.html', context)


@transaction.atomic
def share_success(request, **kwargs):
    share_obj = Share.objects.select_for_update().order_by('-date').first()
    if request.method == 'POST':
        SharingPlantFormset = modelformset_factory(Plant, form=SharePlantsForm)
        SharingToolFormset = formset_factory(ShareToolForm)
        plant_form = SharingPlantFormset(request.POST or None, request.FILES, prefix='plants')
        tool_form = SharingToolFormset(request.POST or None, request.FILES, prefix='tools')
        if request.session.get('city'):
            warehouses = Warehouse.objects.annotate(free_place=Sum(F('capacity') - F('thing_count'))).filter(
                city=request.session['city'])
        else:
            warehouses = Warehouse.objects.annotate(free_place=Sum(F('capacity') - F('thing_count')))
        if plant_form.is_valid() and tool_form.is_valid():
            for form_p in plant_form:
                new_plant = form_p.save(commit=False)
                plants_amount = form_p.cleaned_data.get('amount')
                new_plant.name = new_plant.name.title()
                right_warehouse = warehouses.filter(free_place__gt=plants_amount).first()
                if right_warehouse is None:
                    return redirect('no_place')
                new_plant.warehouse_id = right_warehouse
                new_plant.share_id = share_obj
                new_plant.save()

            for form in tool_form:
                new_tool = form.save(commit=False)
                tools_amount = form.cleaned_data.get('amount')
                right_warehouse = warehouses.filter(free_place__gt=tools_amount).first()
                if right_warehouse is None:
                    return redirect('no_place')
                new_tool.name = new_tool.name.title()
                new_tool.warehouse_id = right_warehouse
                new_tool.share_id = share_obj
                new_tool.save()

        # else:
        #     formset_plant = SharingPlantFormSet(prefix='plants')
        #     formset_tool = SharingToolFormSet(prefix='tools')
        #     context = {'plant_form': formset_plant,
        #                'tool_form': formset_tool}
        #     return render(request, 'share_detail.html', context)

    context = {"share_id": share_obj}
    return render(request, 'share_success.html', context=context)


@login_required
@permission_required('sharing.request_manage', raise_exception=True)
def request_list(request):
    if request.method == 'GET':
        request_objects = Request.objects.filter(requestthing__status='Booked').distinct().order_by('date')
        print(request_objects)
        context = {'request_list': request_objects}
        return render(request, 'request_list_update.html', context)


@login_required
@permission_required('sharing.share_manage', raise_exception=True)
def share_list(request):
    if request.method == 'GET':
        share_objects = Share.objects.filter(sharething__ready_for_save=0).order_by('date')
        context = {'share_list': share_objects}
        return render(request, 'share_list_update.html', context)


@transaction.atomic
def share_update(request, pk):
    share_id = Share.objects.get(id=pk)
    domain = get_domain(request)
    if request.method == 'POST':
        p_form = PlantsFormSet(request.POST, request.FILES, instance=share_id, prefix='plants')
        t_form = ToolsFormSet(request.POST, request.FILES, instance=share_id, prefix='tools')
        if p_form.is_valid() and t_form.is_valid():
            share_id.sharething_set.update(ready_for_save=True)
            p_form.save()
            t_form.save()

        shared_things = share_id.sharething_set.values('name')
        requested_things = RequestThing.objects.filter(status='Requested').values('name').order_by('request_id__date')
        overlap = shared_things.intersection(requested_things)
        overlap_serialized = dumps(list(overlap))
        if overlap.count() != 0:
            user_ids = RequestThing.objects.filter(name__in=overlap).values('request_id__user')
            users = registration.models.User.objects.filter(id__in=user_ids).values('email')
            users_serialized = dumps(list(users))
            send_email_update.delay(domain, users=users_serialized, things=overlap_serialized)
        return redirect('share_list')

    else:
        p_form = PlantsFormSet(instance=share_id, prefix='plants')
        t_form = ToolsFormSet(instance=share_id, prefix='tools')

    context = {
        'plants_form': p_form,
        'tools_form': t_form
    }

    return render(request, 'share_update.html', context)


@cache_page(CACHE_TTL)
def sharing_things(request):
    if request.method == 'GET':
        tool_objects = Tool.objects.filter(ready_for_save=True)
        context = {'things': tool_objects}
        return render(request, 'share_tool_list.html', context)


@cache_control(public=True)
@cache_page(CACHE_TTL)
def sharing_plants(request):
    if request.method == 'GET':
        plants_objects = Plant.objects.filter(ready_for_save=True, amount__gt=0)
        degrees = CarePlant.objects.values('growing_difficulty').distinct()
        degree_value = [v.get('growing_difficulty') for v in degrees]
        types = TypePlant.objects.all()
        fruit = Plant.objects.values('fruit').distinct()
        fruit_value = [v.get('fruit') for v in fruit]
        places = Plant.objects.values('place_of_growth').distinct()
        place_value = [v.get('place_of_growth') for v in places]
        fruit = request.GET.get('fruit')
        place = request.GET.get('place')
        degree = request.GET.get('degree')
        type_id = request.GET.get('type')
        if type_id:
            plants = plants_objects.filter(type_id=type_id)
        elif fruit:
            plants = plants_objects.filter(fruit=fruit)
        elif place:
            plants = plants_objects.filter(place_of_growth=place)
        elif degree:
            plants = plants_objects.filter(careplant__growing_difficulty=degree)
        else:
            plants = plants_objects

        context = {'things': plants,
                   'types': types,
                   'fruit': fruit_value,
                   'places': place_value,
                   'degree': degree_value,
                   }

        # data = cartData(request)
        # items = data['items']
        # order = data['order']
        # cartItems = data['cartItems']
        #
        # products = Product.objects.all()
        # return render(request, "index.html", {'products': products, 'cartItems': cartItems})

        return render(request, 'share_plant_list.html', context)


class PlantDetailView(generic.DetailView):
    model = Plant
    template_name = 'plant_detail.html'
    context_object_name = 'plant'


class ToolDetailView(generic.DetailView):
    model = Tool
    template_name = 'tool_detail.html'
    context_object_name = 'tool'


@transaction.atomic
@decorators.login_required
def request_detail(request):
    if request.POST.get('request'):
        request_abstract = Request.objects.create(thing_amount=request.POST.get('request'), user=request.user)
        thing_amount = int(request_abstract.thing_amount)
        RequestFormSet = formset_factory(RequestThingForm,
                                         extra=thing_amount)
        context = {
            'thing_form': RequestFormSet(),
        }
        return render(request, 'request_detail.html', context)


@transaction.atomic
def request_success(request, **kwargs):
    request_obj = Request.objects.select_for_update().order_by('-date').first()
    plants = Plant.objects.all()
    tools = Tool.objects.all()
    goods = list(chain(plants, tools))
    name = []
    if request.method == 'POST':

        RequestFormSet = modelformset_factory(RequestThing, RequestThingForm)
        thing_form = RequestFormSet(request.POST or None)
        if request.session.get('city'):
            warehouse = Warehouse.objects.filter(
                city=request.session['city']).first()
        else:
            warehouse = Warehouse.objects.first()
        if thing_form.is_valid():
            new_things = thing_form.save(commit=False)
            for new_thing in new_things:
                new_thing.name = new_thing.name.title()
                new_thing.warehouse_id = warehouse
                in_stock = [product for product in goods if product.name == new_thing.name]
                if in_stock and in_stock[0].amount >= new_thing.amount:
                    name.append(in_stock[0])
                else:
                    new_thing.status = 'Requested'
                    new_thing.request_id = request_obj
                    new_thing.save()
    new_things = request_obj.requestthing_set.all()
    context = {'request_id': request_obj, 'goods': name, 'new_things': new_things}
    return render(request, 'request_success.html', context=context)


@transaction.atomic
def request_update(request, pk):
    request_id = Request.objects.get(id=pk)
    if request.method == 'POST':
        request_form = RequestUpdateForm(request.POST, request.FILES, instance=request_id)
        thing_form = RequestThingFormSet(request.POST, instance=request_id)
        print(request_form.is_valid(), thing_form.is_valid())
        if request_form.is_valid() and thing_form.is_valid():
            request = request_form.save(commit=False)
            request.requestthing_set.update(status='Shipped')
            request_form.save()
        return redirect('request_list')

    else:
        request_form = RequestUpdateForm(instance=request_id)
        thing_form = RequestThingFormSet(instance=request_id)

    context = {
        'request_form': request_form,
        'thing_form': thing_form
    }
    return render(request, 'request_update.html', context)


class RequestView(generic.ListView):
    model = RequestThing
    template_name = 'request_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        things = RequestThing.objects.filter(status='Requested')
        filtered_things = things.order_by('name'). \
            values('name').annotate(total=Sum('amount'))
        print(filtered_things)
        context['request_list'] = filtered_things
        return context


@login_required
def cart_add(request, id):
    cart = Cart(request)
    cart.add(product=get_product(id))
    return redirect("home")


@login_required
def item_clear(request, id):
    cart = Cart(request)
    cart.remove(get_product(id))
    return redirect("cart_detail")


@login_required
def item_increment(request, id):
    cart = Cart(request)
    for key, value in request.session['cart'].items():
        if key == str(id):
            dict_key = request.session['cart'].get(key)
            print(dict)
            requested_value = dict_key.get('amount')
            product = get_product(id)
            if product.amount - 1 >= requested_value:
                cart.add(product=get_product(id))
            else:
                return render(request, 'no_amount.html', context={'amount': product.amount})
    return redirect("cart_detail")


@login_required
def item_decrement(request, id):
    cart = Cart(request)
    cart.decrement(product=get_product(id))
    return redirect("cart_detail")


@login_required
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required
def cart_detail(request):
    return render(request, 'cart.html')


@login_required
def orders(request):
    if request.method == 'GET':
        things = RequestThing.objects.filter(request_id__user=request.user)
        requested_items = things.filter(status='Requested')
        shipped_items = things.filter(status='Shipped')
        return render(request, 'users_requests.html', context={'requested_items': requested_items,
                                                               'shipped_items': shipped_items})


@transaction.atomic()
@login_required
def checkout(request):
    ids = []
    for k in request.session['cart'].keys():
        ids.append(k)
    address = request.POST.get('address')
    phone = request.POST.get('phone')
    print(phone, address)
    items = ShareThing.objects.filter(id__in=ids)
    request_id = Request.objects.create(user=request.user,
                                        thing_amount=len(request.session['cart']), city=request.session['city'],
                                        address=address,
                                        phone=phone)
    for item in items:
        for key, value in request.session['cart'].items():
            if key == str(item.id):
                dict_key = request.session['cart'].get(key)
                requested_value = dict_key.get('amount')
                item.amount -= requested_value
                item.save()
                request_thing = RequestThing(name=item.name, amount=requested_value, status='Booked',
                                             request_id=request_id,
                                             warehouse_id=item.warehouse_id)
                request_thing.save()

    request.session['cart'] = {}
    return render(request, 'thank_you.html', context={'request_id': request_id.id})
