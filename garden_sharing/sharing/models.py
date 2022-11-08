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
    class Meta:
        permissions = (
                       ("share_manage", "Can view and process users shares"),
                       )
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    plants_amount = models.IntegerField(default=0, null=True)
    thing_amount = models.IntegerField(default=0, null=True)
    user = models.ForeignKey(registration.models.User,
                             on_delete=models.CASCADE, default=19)
    date = models.DateTimeField(default=timezone.now)


class Request(models.Model):
    class Meta:
        permissions = (
                       ("request_manage", "Can view and process users requests"),
                       )
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    user = models.ForeignKey(registration.models.User,
                             on_delete=models.CASCADE, default=19)
    thing_amount = models.IntegerField(default=0)
    city = models.CharField(max_length=20, default='Minsk')
    address = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=50, default='', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    @property
    def booked_items(self):
        items = self.requestthing_set.filter(status='Booked')
        print(items)
        return items


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
        quantity_thing = self.sharething_set.aggregate(models.Sum('amount'))
        if quantity_thing['amount__sum'] is None:
            return self.capacity
        else:
            return self.capacity - quantity_thing['amount__sum']


class Thing(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=30, blank=False)
    amount = models.IntegerField()
    warehouse_id = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ShareThing(Thing):
    share_id = models.ForeignKey(Share, on_delete=models.CASCADE, null=True)
    ready_for_save = models.BooleanField(choices=((0, 'Not ready '), (1, 'Ready')), default=0)


class RequestThing(Thing):
    STATUS_CHOICE = [('Requested', 'Requested'),
                     ('Shipped', 'Shipped'),
                     ('Booked', 'Booked')]
    status = models.CharField(max_length=100, choices=STATUS_CHOICE, default='Requested')
    request_id = models.ForeignKey(Request, on_delete=models.CASCADE)


class TypePlant(models.Model):
    name = models.CharField(max_length=30, blank=False)
    PLANTS_CATEGORY = [('Tree/Bush', 'Tree/Bush'),
                       ('Flower', 'Flower'),
                       ]
    category = models.CharField(max_length=10, choices=PLANTS_CATEGORY, default='Tree/Bush')
    description = RichTextField(null=True, blank=True)

    def __str__(self):
        return self.name


# class RequestThing(Thing):
#     STATUS_CHOICE = [('Requested', 'Requested'),
#                      ('Shipped', 'Shipped')]
#     status = models.CharField(max_length=100, choices=STATUS_CHOICE, default='Requested')


class Plant(ShareThing):
    common_details = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='images', blank=True)
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


class Video(models.Model):
    video = models.FileField(upload_to='videos_uploaded', blank=True, max_length=200,
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    frames = models.FloatField(null=True)
    rate = models.FloatField(null=True)

    plant = models.OneToOneField(Plant, on_delete=models.SET_NULL, blank=True, null=True)


class CarePlant(models.Model):
    lighting = models.CharField(max_length=20)
    watering = models.CharField(max_length=20)
    transplant = models.CharField(max_length=40)
    temperature = models.CharField(max_length=20)
    GROWING_DIFFICULTY = [('Low', 'requires constant monitoring'),
                          ('Medium', 'requires care 1 time in 1-2 weeks'),
                          ('High', 'requires care 1 time in 2-3 weeks'),
                          ]
    growing_difficulty = models.CharField(max_length=100, choices=GROWING_DIFFICULTY,
                                          default='Low')
    plant = models.OneToOneField(Plant, on_delete=models.CASCADE, blank=True, null=True)


def create_care_description(sender, instance, created, **kwargs):
    if created:
        CarePlant.objects.create(plant=instance)
        instance.careplant.save()


models.signals.post_save.connect(receiver=create_care_description, sender=Plant)


class Tool(ShareThing):
    common_details = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='images', null=True)


@receiver(post_save, sender=Plant)
@receiver(post_save, sender=Tool)
def stocked_warehouse(sender, instance, **kwargs):
    actual_amount = instance.warehouse_id.sharething_set.aggregate(models.Sum('amount'))
    instance.warehouse_id.thing_count = actual_amount['amount__sum']
    instance.warehouse_id.save()
