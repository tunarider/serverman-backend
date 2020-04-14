from rest_framework import viewsets, mixins
from .models import (
    Environment,
    Network,
    Ip,
    Device,
)
from .serializers import (
    DeviceSerializer,
    EnvironmentSerializer,
    NetworkSerializer,
    IpSerializer,
    BareMetal
)


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        queryset = Device.objects.all()
        is_hypervisor = self.request.query_params.get('hypervisor_only', None)
        if is_hypervisor is not None:
            baremetals = BareMetal.objects.filter(is_hypervisor=True)
            queryset = Device.objects.filter(
                object_id__in=baremetals
            )
        return queryset


class EnvironmentViewSet(viewsets.ModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer


class IpViewSet(mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):
    queryset = Ip.objects.all()
    serializer_class = IpSerializer

