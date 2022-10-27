from itertools import chain

from django.db.models import Sum, F
from django.forms import formset_factory, modelformset_factory
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import decorators
from django.views import generic
from .forms import SharePlantsForm, ShareToolForm, \
    ToolsFormSet, PlantsFormSet, RequestThingForm
from .models import Warehouse, Share, SharingPlant, SharingTool, TypePlant, CarePlant, Request, RequestThing
from django.db import transaction


def set_city_session(request):
    request.session['city'] = request.POST['city']
    print(request.session['city'])
    return redirect(reverse('home'))


def home_page(request):
    if request.session.get('city'):
        warehouse = Warehouse.objects.filter(city=request.session['city']).first()
    else:
        warehouse = Warehouse.objects.all().first().id
    # occupied_place = warehouse.thing_count
    # share_disabled = occupied_place >= warehouse.capacity
    context = {
        "warehouse": warehouse
        # "disabled": share_disabled,
        # "warehouse": warehouse,
    }
    return render(request, 'index.html', context)


@transaction.atomic
def share_success(request, **kwargs):
    share_obj = Share.objects.select_for_update().order_by('-date').first()
    if request.method == 'POST':
        SharingPlantFormset = modelformset_factory(SharingPlant, form=SharePlantsForm)
        SharingToolFormset = formset_factory(ShareToolForm)
        plant_form = SharingPlantFormset(request.POST or None, request.FILES, prefix='plants')
        tool_form = SharingToolFormset(request.POST or None, request.FILES, prefix='tools')
        if request.session.get('city'):
            warehouses = Warehouse.objects.annotate(free_place=Sum(F('capacity') - F('thing_count'))).filter(
                city=request.session['city'])
        else:
            warehouses = Warehouse.objects.all()
        if plant_form.is_valid() and tool_form.is_valid():
            for form_p in plant_form:
                new_plant = form_p.save(commit=False)
                plants_amount = form_p.cleaned_data.get('amount')
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


def request(request):
    pass


def request_list(request):
    return None


def share_list(request):
    if request.method == 'GET':
        share_objects = Share.objects.order_by('date')
        context = {'share_list': share_objects}
        return render(request, 'share_list_update.html', context)


def sharing_things(request):
    if request.method == 'GET':
        tool_objects = SharingTool.objects.filter(ready_for_save=True, status='Available')
        context = {'things': tool_objects}
        return render(request, 'share_tool_list.html', context)


def sharing_plants(request):
    if request.method == 'GET':
        plants_objects = SharingPlant.objects.filter(ready_for_save=True, status='Available')
        degrees = CarePlant.objects.values('growing_difficulty').distinct()
        degree_value = [v.get('growing_difficulty') for v in degrees]
        types = TypePlant.objects.all()
        fruit = SharingPlant.objects.values('fruit').distinct()
        fruit_value = [v.get('fruit') for v in fruit]
        places = SharingPlant.objects.values('place_of_growth').distinct()
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
                   'degree': degree_value}
        return render(request, 'share_plant_list.html', context)


class PlantDetailView(generic.DetailView):
    model = SharingPlant
    template_name = 'plant_detail.html'
    context_object_name = 'plant'


class ToolDetailView(generic.DetailView):
    model = SharingTool
    template_name = 'tool_detail.html'
    context_object_name = 'tool'


@transaction.atomic
def share_update(request, pk):
    share_id = Share.objects.get(id=pk)

    if request.method == 'POST':
        p_form = PlantsFormSet(request.POST, request.FILES, instance=share_id, prefix='plants')
        t_form = ToolsFormSet(request.POST, request.FILES, instance=share_id, prefix='tools')
        if p_form.is_valid() and t_form.is_valid():
            update_plants = p_form.save(commit=False)
            for update_plant in update_plants:
                update_plant.ready_for_save = True
                update_plant.save()

            update_tools = t_form.save(commit=False)
            for update_tool in update_tools:
                update_tool.ready_for_save = True
                update_tool.save()
        return redirect('share_list')

    else:
        p_form = PlantsFormSet(instance=share_id, prefix='plants')
        t_form = ToolsFormSet(instance=share_id, prefix='tools')

    context = {
        'plants_form': p_form,
        'tools_form': t_form
    }
    return render(request, 'share_update.html', context)


def sharing_list(request):
    return None


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
    if request.method == 'POST':
        RequestFormSet = modelformset_factory(RequestThing, RequestThingForm)
        thing_form = RequestFormSet(request.POST or None)
        if request.session.get('city'):
            warehouse = Warehouse.objects.filter(
                city=request.session['city']).first()
        else:
            warehouse = Warehouse.objects.first()
        print(thing_form.is_valid())
        if thing_form.is_valid():
            new_things = thing_form.save(commit=False)
            for new_thing in new_things:
                new_thing.warehouse_id = warehouse
                new_thing.request_id = request_obj
                print(new_thing.request_id)
                new_thing.save()

    context = {"request_id": request_obj}
    return render(request, 'request_success.html', context=context)


class RequestView(generic.ListView):
    model = RequestThing
    template_name = 'request_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request_list'] = RequestThing.objects.order_by('request_id__date')
        return context


def cart(request):
    id = list(request.session.get('cart').keys())
    plants = SharingPlant.objects.filter(id=id)
    tools = SharingTool.objects.filter(id=id)
    things = chain(plants, tools)
    print(things)
    return render(request, 'cart.html', {'things': things})


# def orders(request):
#     user = request.session.get('user')
#     if request.method == 'GET':
#         things_requested = RequestThing.objects.filter(status='Requested', request_id__user=user)
#         print(things_requested)
#         return render(request, 'cart.html', {'requested_things': things_requested})
#
#
# def checkout(request):
#     user = request.session.get('user')
#     cart = request.session.get('cart')
#     keys = cart.keys()
#     print(keys)
#     plants = SharingPlant.objects.filter(id__in=(list(keys)))
#     tools = SharingTool.objects.filter(id__in=(list(keys)))
#     products = chain(plants, tools)
#     print(user, cart, products)
#     for product in products:
#         print(cart.get(str(product.id)))
#         request = Request(user=user,
#                       user__email=email,
#                       thing_amount=cart.get(str(thing.id)))
#         request.save()
#     request.session['cart'] = {}
#
#     return redirect('cart')
