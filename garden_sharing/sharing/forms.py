from django import forms
from .models import Warehouse, SharingTool, SharingPlant, CarePlant, Share, RequestThing
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
        model = SharingTool
        fields = '__all__'


class RequestThingForm(forms.ModelForm):
    class Meta:
        model = RequestThing
        fields = ('name', 'amount')


class ShareToolForm(forms.ModelForm):
    class Meta:
        model = SharingTool
        fields = ('name', 'amount', 'common_details', 'photo')


SharingToolFormSet = formset_factory(ShareToolForm)


class SharePlantsForm(forms.ModelForm):
    class Meta:
        model = SharingPlant
        fields = ('name', 'amount', 'common_details', 'photo')


SharingPlantsFormSet = formset_factory(SharePlantsForm)


class SharingToolsUpdateForm(forms.ModelForm):
    name = forms.CharField(disabled=True)
    amount = forms.IntegerField(disabled=True)
    photo = forms.ImageField(disabled=True)

    class Meta:
        model = SharingTool
        exclude = ('warehouse_id', 'status', 'ready_for_save')


class SharingPlantsUpdateForm(forms.ModelForm):
    name = forms.CharField(disabled=True)
    amount = forms.IntegerField(disabled=True)
    photo = forms.ImageField(disabled=True)

    class Meta:
        model = SharingPlant
        exclude = ('warehouse_id', 'status', 'ready_for_save',)


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


ToolsFormSet = inlineformset_factory(Share, SharingTool, form=SharingToolsUpdateForm, extra=0, can_delete=False)

PlantsFormSet = inlineformset_factory(Share, SharingPlant, form=SharingPlantsUpdateForm, formset=BasePlantsFormset,
                                      can_delete=False, extra=0)

CareFormSet = inlineformset_factory(SharingPlant, CarePlant, form=CarePlantForm, extra=0, can_delete=False)
