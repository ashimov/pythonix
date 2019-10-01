from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login

from django.views.generic.base import TemplateView

from pythonix4.router_api_v1 import router

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api_v1/', include(router.urls, namespace='api_v1')),
    url(r'^$', TemplateView.as_view(template_name="app_client/login.html"), name='index'),
    url(r'^pythonix_admin/', include('pythonix_admin.urls', app_name='pythonix_admin', namespace='pythonix_admin')),
    url(r'^pythonix_client/', include('pythonix_client.urls', app_name='pythonix_client', namespace='pythonix_client')),
    url(r'^logout/$', login, {'template_name': 'app_client/login.html'}, name='logout')
]
