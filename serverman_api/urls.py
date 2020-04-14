from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'environments', views.EnvironmentViewSet)
router.register(r'networks', views.NetworkViewSet)
router.register(r'ips', views.IpViewSet)
router.register(r'devices', views.DeviceViewSet, basename='devices')

urlpatterns = [
    path('', include(router.urls))
]

