from pythonix4.router_api_v1 import router

from api_v1 import views

web_portal_router = router.register('client_groups', views.ClientsGroupViewSet, base_name='client_groups')