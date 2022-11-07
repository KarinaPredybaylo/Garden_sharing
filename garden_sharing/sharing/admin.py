from django.contrib import admin
from .models import Plant, Tool, \
    Share, Request, TypePlant, Warehouse, CarePlant, Thing, RequestThing, Video


@admin.register(Plant)
class SharingPlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'common_details',
                    'warehouse_id', 'ready_for_save',)
    list_filter = ('type_id',)

    def type_plant_name(self, obj):
        return obj.type_id.name

    def care_data(self, obj):
        return obj.care.name

    def category_plant(self, obj):
        return obj.type_id.category

    search_fields = ('name__startswith',)
    fieldsets = (
        ('Common_info', {
            'fields': ('name', 'amount', 'ready_for_save')
        }),
        ('Details', {
            'fields': ('common_details', 'warehouse_id', 'type_id', 'fruit', 'photo',
                    'share_id')
        }),
    )
    type_plant_name.admin_order_field = 'type_id__name'


class InlinePlant(admin.StackedInline):
    model = Plant
    extra = 0

#
class InlineThing(admin.StackedInline):
    model = RequestThing
    extra = 0


@admin.register(Tool)
class SharingToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'common_details', 'warehouse_id', 'photo', 'ready_for_save')


    def share_date(self, obj):
        return obj.share_id.date

    search_fields = ('name__startswith',)
    fieldsets = (
        ('Common_info', {
            'fields': ('name','amount')
        }),
        ('Details', {
            'fields': ('common_details', 'warehouse_id', 'photo')
        }),
    )
    share_date.admin_order_field = 'share_id__date'


class InlineTool(admin.StackedInline):
    model = Tool
    extra = 0 # amount od extra forms


@admin.register(RequestThing)
class RequestThingAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'amount', 'warehouse_name')
    list_filter = ('status', )

    def warehouse_name(self, obj):
        return obj.warehouse_id.name

    def request_date(self, obj):
        return obj.request_id.date

    search_fields = ('name__startswith',)


@admin.register(TypePlant)
class PlantTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')
    inlines = [InlinePlant, ]
    fieldsets = (
        (None, {
            'fields': ['name']
        }),
        ('Description', {
            'fields': ('category', 'description')
        }),
    )


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'plants_amount', 'thing_amount', 'user')
    inlines = [InlineTool, InlinePlant, ]
    date_hierarchy = 'date'


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'thing_amount', 'user')
    inlines = [InlineThing, ]
    date_hierarchy = 'date'


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'thing_count', 'capacity', 'long', 'lat', 'free_place_amount')

    inlines = [InlineThing, ]


@admin.register(CarePlant)
class SharingPlantAdmin(admin.ModelAdmin):
    list_display = ('lighting', 'transplant', 'temperature', 'watering', 'growing_difficulty')


@admin.register(Video)
class SharingPlantAdmin(admin.ModelAdmin):
    list_display = ('video', 'plant')
