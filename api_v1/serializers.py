from rest_framework import serializers

from pythonix_admin import models

class ClientsGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ClientsGroups
        fields = ['id', 'title']
