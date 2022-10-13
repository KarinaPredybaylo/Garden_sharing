import uuid
from django.utils import timezone
from django.db import models
from django.core.validators import FileExtensionValidator


class Share(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    plants_amount = models.IntegerField(default=0)
    thing_amount = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)


class Request(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    plants_amount = models.IntegerField(default=0)
    thing_amount = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)


class Warehouse(models.Model):
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(thing_count__lte=models.F('capacity')), name='thing_count_lte'),
        ]

    name = models.CharField(max_length=200)
    lat = models.FloatField(db_column='latitude')
    long = models.FloatField(db_column='longitude')
    thing_count = models.IntegerField(default=0, null=True)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


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
    PLANTS_CATEGORY = [('Tree', 'Tree'),
                       ('Bush', 'Bush'),
                       ('Flower', 'Used'),
                       ]
    category = models.CharField(max_length=10, choices=PLANTS_CATEGORY)
    description = models.CharField(max_length=300, blank=False, null=True)

    def __str__(self):
        return self.name


class ShareThing(Thing):
    STATUS_CHOICE = [('Available', 'Available'),
                     ('Booked', 'Booked')]
    status = models.CharField(max_length=100, choices=STATUS_CHOICE, default='Available')
    share_id = models.ForeignKey(Share, on_delete=models.CASCADE)


class RequestThing(Thing):
    STATUS_CHOICE = [('Requested', 'Requested'),
                     ('Shipped', 'Shipped')]
    status = models.CharField(max_length=100, choices=STATUS_CHOICE, default='Requested')
    request_id = models.ForeignKey(Request, on_delete=models.CASCADE)


class CarePlant(models.Model):
    lighting = models.CharField(max_length=10)
    watering = models.CharField(max_length=20)
    transplant = models.CharField(max_length=40)
    temperature = models.CharField(max_length=20)
    GROWING_DIFFICULTY = [('Low', 'requires constant monitoring'),
                          ('Medium', 'requires care 1 time in 1-2 weeks'),
                          ('High', 'requires care 1 time in 2-3 weeks'),
                          ]
    growing_difficulty = models.CharField(max_length=100, choices=GROWING_DIFFICULTY, default='Requested')


class SharingPlant(ShareThing):
    common_details = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='images', blank=True)
    video = models.FileField(upload_to='videos_uploaded', blank=True,
                             validators=[
                                 FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    type_id = models.ForeignKey(TypePlant, on_delete=models.CASCADE)
    care = models.OneToOneField(CarePlant, on_delete=models.CASCADE, blank=True, null=True)


class SharingTool(ShareThing):
    common_details = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='images', null=True)
