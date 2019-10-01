from rest_framework.viewsets import ModelViewSet

from pythonix_admin import models
from api_v1 import serializers
from api_v1 import filters

class ClientsGroupViewSet(ModelViewSet):
    queryset = models.ClientsGroups.objects.all()
    serializer_class = serializers.ClientsGroupSerializer
