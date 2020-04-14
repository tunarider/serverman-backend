from enum import Enum, unique
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey


def django_enum(cls):
    cls.do_not_call_in_templates = True
    return cls


class Environment(models.Model):
    name = models.CharField(max_length=20, db_index=True)
    comment = models.CharField(max_length=1024, blank=True)


class Network(models.Model):
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        db_index=True
    )
    cidr = models.CharField(max_length=18, db_index=True)
    gateway = models.CharField(max_length=15, blank=True)
    comment = models.CharField(max_length=1024, blank=True)


class Ip(models.Model):
    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        db_index=True
    )
    address = models.CharField(max_length=15, db_index=True)
    is_vip = models.BooleanField()
    comment = models.CharField(max_length=1024, blank=True)


class Device(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        db_index=True
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    device_object = GenericForeignKey('content_type', 'object_id')
    ips = models.ManyToManyField(Ip, blank=True)


class Server(models.Model):
    @unique
    @django_enum
    class State(Enum):
        stopped = 'ST'
        running = 'RN'
        fault = 'FA'

    host_name = models.CharField(max_length=64, db_index=True)
    os = models.CharField(max_length=64, blank=True, db_index=True)
    cpu = models.CharField(max_length=64, blank=True)
    memory = models.CharField(max_length=64, blank=True)
    disk = models.CharField(max_length=64, blank=True)
    network = models.CharField(max_length=64, blank=True)
    state = models.CharField(
        max_length=2,
        choices=[(choice.value, choice.name) for choice in State],
        default=State.stopped.value,
        db_index=True,
    )
    comment = models.CharField(max_length=1024, blank=True)
    device = GenericRelation(Device)


class BareMetal(Server):
    is_hypervisor = models.BooleanField()
    serial = models.CharField(max_length=64, blank=True)
    model = models.CharField(max_length=64, blank=True)


class VirtualMachine(Server):
    hypervisor = models.ForeignKey(BareMetal, on_delete=models.CASCADE)
