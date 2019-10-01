from django.conf.urls import include, url
from django.contrib import admin
from pythonix_admin import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^$', views.AdminIndexPage.as_view(), name='admin_index'),
    url(r'^create_client/$', views.CreateClient.as_view(), name='create_client'),
    url(r'^get_free_ipaddress/(\d{1,9})/$', login_required(views.get_free_ipaddress, login_url='/admin/'), name='get_free_ipaddress'),
    url(r'^abbreviation_physical_network/(\d{1,9})/$', views.abbreviation_physical_network, name='abbreviation_physical_network'),
    url(r'^get_streets/(\d{1,9})/$', login_required(views.get_streets, login_url='/admin/'), name='get_streets'),
    url(r'^client_list/(?P<pk>\d+)/$', login_required(views.ClientsList.as_view(), login_url='/admin/'), name='client_list'),
    url(r'^client_info/(?P<pk>\d+)/$', views.ClientInfoView.as_view(), name='client_info'),
    url(r'^del_client/(?P<pk>\d+)/$', views.ClientDelete.as_view(), name='del_client'),
    url(r'^pay_balance/(\d{1,9})/(\d{1,9})/(\d{1,9})/$', views.pay_balance, name='pay_balance'),
    url(r'^client_on_off/(\d{1,9})/(\d{1,9})/$', views.client_on_off, name='client_on_off'),
    url(r'^get_status_client/(\d{1,9})/$', views.getStatusClient, name='get_status_client'),
    url(r'^get_pon_info_client/(\d{1,9})/$', views.get_pon_info_client, name='get_pon_info_client'),
    #url(r'^migrates/$', views.migrates, name='migrates'),
    url(r'^get_client_groups/(\d{1,9})/$', views.get_client_groups, name='get_client_groups'),
    url(r'^client_connection_list/(?P<pk>\d+)/$', login_required(views.ClientsConnectionList.as_view(), login_url='/admin/'),name='client_connection_list'),
    url(r'^update_password/(\d{1,9})/$', views.update_password, name='update_password'),
    url(r'^create_order/$', views.CreateOrder.as_view(), name='create_order'),
    url(r'^order_info/(?P<pk>\d+)/$', views.OrderInfoView.as_view(), name='order_info'),
    url(r'^send_sms_info_client_ajax/(\d{1,9})/(\d{1,9})/$', views.send_sms_info_client_ajax, name='send_sms_info_client_ajax'),
    url(r'^payment_from_pay_systems/$', views.payment_from_pay_systems, name='payment_from_pay_systems'),
]