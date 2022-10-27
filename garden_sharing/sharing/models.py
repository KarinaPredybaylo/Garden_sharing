import uuid
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
import registration.models


class Share(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    plants_amount = models.IntegerField(default=0, null=True)
    thing_amount = models.IntegerField(default=0, null=True)
    user = models.ForeignKey(registration.models.User,
                             on_delete=models.CASCADE, default=19)
    date = models.DateTimeField(default=timezone.now)


class Request(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    user = models.ForeignKey(registration.models.User,
                             on_delete=models.CASCADE, default=19)
    thing_amount = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)


class Warehouse(models.Model):
    class Meta:
        # thing_count = self.sharething_set.filter(status='Available').aggregate(models.Sum('amount'))
        constraints = [
            models.CheckConstraint(check=models.Q(thing_count__lte=models.F('capacity')), name='thing_count_lte'),
        ]

    name = models.CharField(max_length=200)
    city = models.CharField(max_length=20, default='Minsk')
    lat = models.FloatField(db_column='latitude')
    long = models.FloatField(db_column='longitude')
    thing_count = models.IntegerField(default=0, null=True)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

    def free_place_amount(self):
        number_thing = self.sharething_set.filter(status='Available').aggregate(models.Sum('amount'))
        if number_thing['amount__sum'] is None:
            return self.capacity
        else:
            return self.capacity - number_thing['amount__sum']

        # def occupied_place(self):
        #     self.objects.aggregate(common_number=)


class Thing(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=30, blank=False)
    amount = models.IntegerField()
    warehouse_id = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TypePlant(models.Model):
    name = models.CharField(max_length=30, blank=False)
    PLANTS_CATEGORY = [('Tree/Bush', 'Tree/Bush'),
                       ('Flower', 'Flower'),
                       ]
    category = models.CharField(max_length=10, choices=PLANTS_CATEGORY, default='Tree/Bush')
    description = RichTextField(null=True, blank=True)

    def __str__(self):
        return self.name


class ShareThing(Thing):
    STATUS_CHOICE = [('Available', 'Available'),
                     ('Booked', 'Booked')]
    status = models.CharField(max_length=100, choices=STATUS_CHOICE, default='Available')
    share_id = models.ForeignKey(Share, on_delete=models.CASCADE, null=True)
    ready_for_save = models.BooleanField(choices=((0, 'Not ready '), (1, 'Ready')), default=0)


class RequestThing(Thing):
    STATUS_CHOICE = [('Requested', 'Requested'),
                     ('Shipped', 'Shipped')]
    status = models.CharField(max_length=100, choices=STATUS_CHOICE, default='Requested')
    request_id = models.ForeignKey(Request, on_delete=models.CASCADE)


class SharingPlant(ShareThing):
    common_details = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='images', blank=True)
    video = models.FileField(upload_to='videos_uploaded', blank=True,
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    type_id = models.ForeignKey(TypePlant, on_delete=models.CASCADE, null=True)
    fruit = models.CharField(max_length=20,
                             choices=[('Fruit', 'Fruit'), ('Not Fruit', 'Not Fruit')], default='Not Fruit'
                             )
    PLACE = [('Garden', 'Garden'),
             ('Room', 'Room'),
             ('Garden and room', 'Garden and room')]
    place_of_growth = models.CharField(choices=PLACE, max_length=20, default='Garden')

    def get_absolute_url(self):
        return reverse('plants_update', args=[str(self.id)])


class CarePlant(models.Model):
    lighting = models.CharField(max_length=10)
    watering = models.CharField(max_length=20)
    transplant = models.CharField(max_length=40)
    temperature = models.CharField(max_length=20)
    GROWING_DIFFICULTY = [('Low', 'requires constant monitoring'),
                          ('Medium', 'requires care 1 time in 1-2 weeks'),
                          ('High', 'requires care 1 time in 2-3 weeks'),
                          ]
    growing_difficulty = models.CharField(max_length=100, choices=GROWING_DIFFICULTY,
                                          default='requires constant monitoring')
    plant = models.OneToOneField(SharingPlant, on_delete=models.CASCADE, blank=True, null=True)


def create_care_description(sender, instance, created, **kwargs):
    if created:
        CarePlant.objects.create(plant=instance)
        instance.careplant.save()


models.signals.post_save.connect(receiver=create_care_description, sender=SharingPlant)


class SharingTool(ShareThing):
    common_details = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='images', null=True)


# @receiver(post_save, sender=SharingTool)
# def stocked_warehouse(sender, instance, **kwargs):
#     actual_amount = sender.objects.filter(status='Available',
#                                           warehouse_id=instance.warehouse_id).aggregate(models.Sum('amount'))
#     print(actual_amount['amount__sum'])
#     instance.warehouse_id.tool_count = actual_amount['amount__sum']
#     instance.warehouse_id.save()


# models.signals.post_save.connect(receiver=stocked_warehouse, sender=SharingTool)
# models.signals.post_save.connect(receiver=stocked_warehouse, sender=SharingPlant)


@receiver(post_save, sender=SharingPlant)
@receiver(post_save, sender=SharingTool)
def stocked_warehouse(sender, instance, **kwargs):
    actual_amount = instance.warehouse_id.sharething_set.filter(status='Available').aggregate(models.Sum('amount'))
    instance.warehouse_id.thing_count = actual_amount['amount__sum']
    instance.warehouse_id.save()
