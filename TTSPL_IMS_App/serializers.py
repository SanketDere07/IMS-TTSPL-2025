from rest_framework import serializers
from .models import Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'details', 'status', 'created_at']
        read_only_fields = ['created_at']  # created_at is automatically set, no need to serialize
