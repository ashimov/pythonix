from django.conf.urls import url

from pythonix_client import views


urlpatterns = [
    url(r'^$', views.ClientIndexPage.as_view(), name='client_index'),
    url(r'^client_login/$', views.client_login, name='client_login'),
    url(r'^my_login/$', views.my_login, name='my_login'),
    url(r'^close_order/$', views.close_order, name='close_order'),
]