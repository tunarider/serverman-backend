from collections import OrderedDict
from netaddr import IPNetwork
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject
from generic_relations.relations import GenericRelatedField

from .models import (
    Environment,
    Network,
    Ip,
    Device,
    BareMetal,
    VirtualMachine,
)


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = (
            'id',
            'name',
            'comment'
        )


class NetworkSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            elif field.field_name == 'environment':
                env = field.queryset.get(pk=attribute.pk)
                env_serializer = EnvironmentSerializer(env)
                ret[field.field_name] = env_serializer.data['name']
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret

    def create(self, validated_data):
        network = Network.objects.create(**validated_data)
        for ip in IPNetwork(network.cidr):
            Ip.objects.create(
                network=network,
                address=ip,
                is_vip=False,
            )
        return network

    class Meta:
        model = Network
        fields = (
            'id',
            'environment',
            'cidr',
            'gateway',
            'comment'
        )


class BareMetalSerializer(serializers.ModelSerializer):
    class Meta:
        model = BareMetal
        fields = '__all__'


class VirtualMachineSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            elif field.field_name == 'hypervisor':
                hv = field.queryset.get(pk=attribute.pk)
                hv_serializer = BareMetalSerializer(hv)
                ret[field.field_name] = hv_serializer.data
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret

    class Meta:
        model = VirtualMachine
        fields = '__all__'


class DeviceSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model',
    )
    device_object = GenericRelatedField({
        BareMetal: BareMetalSerializer(),
        VirtualMachine: VirtualMachineSerializer(),
    })
    ips = serializers.PrimaryKeyRelatedField(
        queryset=Ip.objects.all(),
        many=True,
        required=False
    )

    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            elif field.field_name == 'environment':
                env = field.queryset.get(pk=attribute.pk)
                env_serializer = EnvironmentSerializer(env)
                ret[field.field_name] = env_serializer.data
            elif field.field_name == 'ips' and attribute:
                ret[field.field_name] = [
                    IpSerializer(value).data
                    for value in attribute
                ]
            else:
                ret[field.field_name] = field.to_representation(attribute)
        return ret

    def create(self, validated_data):
        raw = validated_data.pop('device_object')
        if validated_data.get("content_type").model_class() == BareMetal:
            device_object = BareMetal(**raw)
        elif validated_data.get("content_type").model_class() == VirtualMachine:
            device_object = VirtualMachine(**raw)
        else:
            raise Exception('Unexpected type of device object')
        device_object.save()
        instance = Device(
            name=validated_data.get('name'),
            content_type=validated_data.get('content_type'),
            environment=validated_data.get('environment'),
            device_object=device_object,
        )
        instance.save()
        instance.ips.set(validated_data.get('ips', instance.ips))
        return instance

    def update(self, instance, validated_data):
        raw = validated_data.pop('device_object')
        if instance.content_type.model_class() == BareMetal:
            device_object, created = BareMetal.objects.get_or_create(
                id=instance.device_object.id,
                defaults=raw
            )
        elif instance.content_type.model_class() == VirtualMachine:
            device_object, created = VirtualMachine.objects.get_or_create(
                id=instance.device_object.id,
                defaults=raw
            )
        else:
            raise Exception('Unexpected type of device object')
        if not created:
            for k, v in raw.items():
                setattr(device_object, k, v)
                device_object.save()
        instance.name = validated_data.get('name', instance.name)
        instance.environment = validated_data.get(
            'environment',
            instance.environment
        )
        instance.ips.set(validated_data.get('ips', instance.ips))
        instance.save()
        return instance

    class Meta:
        model = Device
        fields = (
            'id',
            'name',
            'environment',
            'content_type',
            'device_object',
            'ips',
        )


class IpSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            elif field.field_name == 'network':
                net = Network.objects.get(pk=attribute.pk)
                ret['network'] = {
                    'id': net.id,
                    'cidr': net.cidr,
                    'environment': {
                        'id': net.environment.id,
                        'name': net.environment.name
                    }
                }
            else:
                ret[field.field_name] = field.to_representation(attribute)

        devices = tuple(instance.device_set.all())
        ret['devices'] = [
            {
                'id': device.id,
                'name': device.name,
                'host_name': device.device_object.host_name
            }
            for device in devices
        ]
        return ret

    class Meta:
        model = Ip
        fields = (
            'id',
            'network',
            'address',
            'is_vip',
            'comment'
        )
        read_only_fields = (
            'id',
            'network',
            'address'
        )
