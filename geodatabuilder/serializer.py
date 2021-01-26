from django.contrib.auth.models import GeodataBuilder
from rest_framework import serializers


class GeodataBuilderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GeodataBuilder

