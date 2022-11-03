from django import forms
from .models import Warehouse, Tool, Plant, CarePlant, Share, Thing, RequestThing, Request
from django.forms import formset_factory, BaseInlineFormSet, inlineformset_factory


class WarehouseForm(forms.Form):
    type_cities = [(i['city'], i['city']) for i in Warehouse.objects.values('city').distinct()]
    city = forms.ChoiceField(choices=type_cities)


class CarePlantForm(forms.ModelForm):
    class Meta:
        model = CarePlant
        fields = '__all__'


class ToolsUpdateForm(forms.ModelForm):
    class Meta:
        model = Tool
        exclude = ('id',)


class RequestThingForm(forms.ModelForm):
    class Meta:
        model = RequestThing
        fields = ('name', 'amount')


class RequestThingUpdateForm(forms.ModelForm):
    name = forms.CharField(disabled=True)
    amount = forms.CharField(disabled=True)

    class Meta:
        model = RequestThing
        exclude = ('id', 'warehouse_id', 'status')


class ShareToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ('name', 'amount', 'common_details', 'photo')


SharingToolFormSet = formset_factory(ShareToolForm)


class SharePlantsForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ('name', 'amount', 'common_details', 'photo')


SharingPlantsFormSet = formset_factory(SharePlantsForm)


class SharingToolsUpdateForm(forms.ModelForm):
    name = forms.CharField(disabled=True)
    amount = forms.IntegerField(disabled=True)
    photo = forms.ImageField(disabled=True)

    class Meta:
        model = Tool
        exclude = ('warehouse_id', 'status', 'ready_for_save', 'request_id')


class SharingPlantsUpdateForm(forms.ModelForm):
    name = forms.CharField(disabled=True)
    amount = forms.IntegerField(disabled=True)
    photo = forms.ImageField(disabled=True)

    class Meta:
        model = Plant
        exclude = ('warehouse_id', 'status', 'ready_for_save', 'request_id')


class BasePlantsFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(BasePlantsFormset, self).add_fields(form, index)

        form.nested = CareFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='careplant-%s-%s' % (
                form.prefix,
                CareFormSet.get_default_prefix()))

    def is_valid(self):
        result = super(BasePlantsFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result

    def save(self, commit=True):

        result = super(BasePlantsFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=True)

        return result


class RequestUpdateForm(forms.ModelForm):

    class Meta:
        model = Request
        exclude=('id',)


RequestThingFormSet = inlineformset_factory(Request, RequestThing, form=RequestThingUpdateForm, can_delete=False, extra=0)

ToolsFormSet = inlineformset_factory(Share, Tool, form=SharingToolsUpdateForm, extra=0, can_delete=False)

PlantsFormSet = inlineformset_factory(Share, Plant, form=SharingPlantsUpdateForm, formset=BasePlantsFormset,
                                      can_delete=False, extra=0)

CareFormSet = inlineformset_factory(Plant, CarePlant, form=CarePlantForm, extra=0, can_delete=False)
