from django.contrib import admin
from . import models

admin.site.register(models.Environment)
admin.site.register(models.Network)
admin.site.register(models.Ip)
admin.site.register(models.Device)
admin.site.register(models.Server)
admin.site.register(models.BareMetal)
admin.site.register(models.VirtualMachine)
