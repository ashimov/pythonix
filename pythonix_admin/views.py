__author__ = 'Jeka'
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import HttpResponseForbidden
from django.views.generic import ListView, CreateView, FormView, UpdateView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from django import forms
from django.core.validators import ip_address_validators
from django.views.decorators.csrf import csrf_exempt
from dateutil.relativedelta import relativedelta
from django.conf import settings

import datetime
from django.core.mail import EmailMessage

from pythonix_admin.smsc_api import SMSC

from pythonix_admin import iplib


from pythonix_admin import models
from scripts.action_mikrotik import ActionMikroTik
from scripts.pon import PonSNMP
import pythonix_admin.forms

from pythonix_admin import bl
from netaddr import EUI


class BaseAdminContentMixin(View):

    @method_decorator(login_required(login_url='/admin/'))
    def dispatch(self, request, *args, **kwargs):
        try:
            request.user.profile_employee
            if self.method_to_view not in models.Employee.ROLE_METHODS[request.user.profile_employee.permissions_role]:
                return HttpResponseForbidden()
        except:
            if self.request.user.is_superuser == False:
                return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class AdminIndexPage(BaseAdminContentMixin, ListView):
    method_to_view = 'show'
    model = models.Clients
    template_name = 'app_admin/index.html'

    def get_context_data(self, **kwargs):
        context = super(AdminIndexPage, self).get_context_data(**kwargs)
        context['orders'] = models.Order.objects.filter(close=False)
        return context


class CreateClient(BaseAdminContentMixin, CreateView):
    method_to_view = 'add'
    model = models.Clients
    fields = ['ip_address', 'ipv6_address', 'send_sms', 'select_tarif', 'select_clients_group', 'select_street', 'mobile_phone',
                'home_address', 'balance', 'login', 'mac_address', 'onu_mac_address']
    template_name = 'app_admin/create_client.html'
    success_url = '/'

    def get_success_url(self):
        self.success_url = '/'
        return super(CreateClient, self).get_success_url()

    @transaction.atomic
    def form_valid(self, form):
        print('VALID')
        password = get_random_string(9, '1234567890')
        self.object = form.save(commit=False)

        print(dir(self.object))
        if models.Clients.objects.filter(select_clients_group_id=self.object.select_clients_group_id, ip_address=self.object.ip_address).count() > 0:
            form._errors.setdefault("ip_address", 'IP адрес занят')
            return self.form_invalid(form)

        try:
            user = User.objects.create_user(username=self.object.login,
                                        email='{}@{}'.format(self.object.login, 'kvazarlink.net'),
                                        password=password, is_staff=True)
        except:
            form._errors.setdefault("login", 'Логин занят')
            return self.form_invalid(form)

        self.object.key = password
        self.object.user = user

        super().form_valid(form)
        print(self.request.user.profile_employee)
        models.Order.objects.create(creator=self.request.user.profile_employee,
                                    executor=self.request.user.profile_employee, client=self.object)
        models.DeferredActionsWithClient.objects.create(action='create', client=self.object)
        return redirect(reverse_lazy('pythonix_admin:client_info', kwargs={'pk':self.object.id}))


# Определяем свободные IP для выбранных подсетей
def get_free_ipaddress(request, id):

    clients_group = models.ClientsGroups.objects.get(id=id)

    clients_used_ip = [client.ip_address for client in models.Clients.objects.filter(select_clients_group=clients_group, deleted_user=False)]
    json_ip_addresses = {}

    for network in clients_group.ipv4networks_list.all():

        for ip_address in iplib.CIDR(str(network.ipv4networks) + "/" + str(network.CIDR)):
            if ip_address not in clients_used_ip and ip_address != network.ipv4networks:
                json_ip_addresses.update({str(ip_address):str(ip_address)})
                break

    return JsonResponse(json_ip_addresses)


# Возвращяем абривиатуру физической сети
def abbreviation_physical_network(request, id):
    json_abbreviation = {}
    physical_network = models.PhysicalNetwork.objects.get(id=id)
    json_abbreviation.update({'abbreviation':physical_network.abbreviation})
    return JsonResponse(json_abbreviation)


# Список улиц
def get_streets(request, id):
    streets = {}
    for street in models.Streets.objects.filter(select_physical_network_id=id):
        streets.update({street.id:street.title})
    return JsonResponse(streets)


# Отображение списка клиентов группы
class ClientsList(BaseAdminContentMixin, ListView):
    method_to_view = 'show'
    model = models.Clients
    template_name = 'app_admin/clients_list.html'
    context_object_name = 'clients_list'

    def get_context_data(self, **kwargs):
        context = super(ClientsList, self).get_context_data(**kwargs)
        context['client_group_id'] = self.kwargs.get('pk')
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(select_clients_group_id=self.kwargs.get('pk'), deleted_user=False)


# Определяем доступные группы клиентов,
def get_client_groups(request, id):
    json_client_groups = {}
    server_list = [server.id for server in models.Servers.objects.filter(physical_network=id)]
    for client_group in models.ClientsGroups.objects.filter(select_server__in=server_list):
        json_client_groups.update({str(client_group.id): u'{}'.format(client_group.title)})
    return JsonResponse(json_client_groups)


# Информация о клиенте
class ClientInfoView(BaseAdminContentMixin, UpdateView):
    method_to_view = 'add'
    success_url = '/pythonix_admin/'
    model = models.Clients
    context_object_name = 'client_info'
    template_name = 'app_admin/client_info.html'

    fields = ['login', 'ip_address', 'ipv6_address', 'send_sms', 'select_tarif',
              'select_clients_group', 'select_street', 'mobile_phone',
                'home_address', 'balance', 'mac_address', 'onu_mac_address']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = models.Employee.objects.filter(permissions_role='ROLE_INSTALLER')
        return context

    def form_valid(self, form):
        if 'add' not in models.Employee.ROLE_METHODS[self.request.user.profile_employee.permissions_role]:
            return redirect(reverse_lazy('pythonix_admin:client_info', kwargs={'pk': self.object.id}))

        client = models.Clients.objects.get(id=self.kwargs["pk"])
        if client.ip_address != form.cleaned_data['ip_address']:
            if models.Clients.objects.filter(ip_address=form.cleaned_data['ip_address'], select_clients_group=client.select_clients_group).count() > 0:
                form._errors.setdefault("ip_address", 'ip address занят')
                return self.form_invalid(form)
            else:
                try:
                    for device in client.select_clients_group.select_server.all():
                        action_mikrotik = ActionMikroTik(device)
                        action_mikrotik.update_ip(client.login, client.ip_address, form.cleaned_data['ip_address'])
                except:
                    form._errors.setdefault("login", 'Сервер не доступен')
                    return self.form_invalid(form)


        if client.login != form.cleaned_data['login']:
            if models.Clients.objects.filter(login=form.cleaned_data['login']).count() > 0:
                form._errors.setdefault("login", 'Логин занят')
                return self.form_invalid(form)
            else:
                try:
                    for device in client.select_clients_group.select_server.all():
                        action_mikrotik = ActionMikroTik(device)
                        action_mikrotik.update_login(client.login, form.cleaned_data['login'])

                    #client.user.username = form.cleaned_data['login']
                    user = User.objects.get(id=client.user.id)
                    user.username = form.cleaned_data['login']
                    user.save()
                except:
                    form._errors.setdefault("login", 'Сервер не доступен')
                    return self.form_invalid(form)

        if form.cleaned_data['select_tarif'].id != client.select_tarif.id:
            try:
                for device in client.select_clients_group.select_server.all():
                    action_mikrotik = ActionMikroTik(device)
                    action_mikrotik.update_tariff(client.login, form.cleaned_data['select_tarif'])
            except:
                form._errors.setdefault("login", 'Сервер не доступен')
                return self.form_invalid(form)

        self.success_url = '/pythonix_admin/client_info/' + self.kwargs["pk"] + '/'
        return super(ClientInfoView, self).form_valid(form)


# Удаление клиента
class ClientDelete(BaseAdminContentMixin, FormView):
    method_to_view = 'delete'
    form_class = pythonix_admin.forms.DelClientForm
    template_name = 'app_admin/delete_client.html'
    success_url = '/pythonix_admin/'

    def get_context_data(self, **kwargs):
        context = super(ClientDelete, self).get_context_data(**kwargs)
        context['client_id'] = self.kwargs.get('pk')
        context['title_message'] = "Удалить клиента"
        return context

    def form_valid(self, form):
        client = models.Clients.objects.get(id=self.kwargs.get('pk'))
        try:
            for device in client.select_clients_group.select_server.all():
                action_mikrotik = ActionMikroTik(device)
                action_mikrotik.delete_user(client.login, client.ip_address)
        except:
            form._errors.setdefault("captcha", 'Устройство не доступно')
            return self.form_invalid(form)

        client.deleted_user = True
        client.save()
        return super(ClientDelete, self).form_valid(form)


# Пополнение баланса
def pay_balance(request, id, sum, temporary_pay):
    try:
        request.user.profile_employee
        if 'pay' not in models.Employee.ROLE_METHODS[request.user.profile_employee.permissions_role]:
            return JsonResponse({'message': 'Пополнение не возможно'})
    except:
        return JsonResponse({'message':'Пополнение не возможно'})

    client = models.Clients.objects.get(id=id)
    json_balance = bl.pay_balance_new(client, request.user, sum, temporary_pay, models.TemporaryPay, models.ReportPayAdmin)
    return JsonResponse(json_balance)


# Включение отключение клиента
def client_on_off(request, id, action):
    try:
        request.user.profile_employee
    except:
        return JsonResponse({'ERROR':'No Admin'})

    client = models.Clients.objects.get(id=id)

    if action == '0':
        client.internet_status = False
        client.save()
        models.DeferredActionsWithClient.objects.create(client=client, action='off')
        return JsonResponse({'message': 'Клиент будет отключен'})
    else:
        client.internet_status = True
        client.save()
        models.DeferredActionsWithClient.objects.create(client=client, action='on')
        return JsonResponse({'message': 'Клиент будет включен'})


# Данные о подключении клиента
def getStatusClient(request, client_id):
    try:
        request.user.profile_employee
    except:
        return JsonResponse({'ERROR':'No Admin'})

    client = models.Clients.objects.get(id=client_id)

    json_status_info = {}

    try:
        arp_records = 0
        for device in client.select_clients_group.select_server.all():
            action_mikrotik = ActionMikroTik(device)
            if action_mikrotik.get_arp(client.ip_address):
                arp_records += 1

        ppp_connect = 0
        for device in client.select_clients_group.select_server.all():
            action_mikrotik = ActionMikroTik(device)
            if action_mikrotik.get_ppp(client.login):
                ppp_connect = action_mikrotik.get_ppp(client.login)

        json_status_info.update({'message': 'Данные получены'})
        if arp_records > 0:
            json_status_info.update({'arp': True})
        else:
            json_status_info.update({'arp': False})

        if ppp_connect != 0:
            json_status_info.update({'ppp':ppp_connect})
        else:
            json_status_info.update({'ppp':False})
    except:
        json_status_info.update({'message':'Сервер не доступен'})

    return JsonResponse(json_status_info)


# Отображение списка подключенных клиентов группы
class ClientsConnectionList(BaseAdminContentMixin, TemplateView):
    method_to_view = 'show'
    template_name = 'app_admin/clients_connection_list.html'
    context_object_name = 'clients_list'

    def get_context_data(self, **kwargs):
        context = super(ClientsConnectionList, self).get_context_data(**kwargs)

        client_group = models.ClientsGroups.objects.get(id=self.kwargs.get('pk'))

        for device in client_group.select_server.all():
            action_mikrotik = ActionMikroTik(device)

        context['ppp_active'] = action_mikrotik.get_ppp_active()

        return context


def migrates(request):
    streets = {}
    import json

    with open('/home/tram/PycharmProjects/pythonix4/pythonix_admin/auth_user.json') as json_data:
        auth_user = json.load(json_data)

    with open('/home/tram/PycharmProjects/pythonix4/pythonix_admin/clients.json') as json_data:
        clients = json.load(json_data)

    for client in clients:
        tarifs = {'2':'1', '3':'2', '4':'3', '5':'4', '6':'5', '7':'6'}
        clients_group = {'1':'1', '2':'2'}


        for userjson in auth_user:
            if clients_group.get(client.get('select_clients_group_id')) != None:
                if userjson.get('id') == client.get('user_ptr_id'):
                    user = User.objects.create_user(username=userjson.get('username'),
                                        email='{}@{}'.format(userjson.get('username'), 'kvazarlink.net'),
                                        password=client.get('key'), is_staff=True)
                    models.Clients.objects.create(user=user, ip_address=client.get('ip_address'),
                        select_tarif_id=tarifs.get(client.get('select_tarif_id')),
                        select_clients_group_id=clients_group.get(client.get('select_clients_group_id')),
                        create_date=client.get('create_date'), end_used_date=client.get('end_used_date'),
                        select_street_id='1', balance=client.get('balance'), internet_status=int(client.get('internet_status')),
                        deleted_user=int(client.get('deleted_user')), key=client.get('key'), login=userjson.get('username'))

    return JsonResponse(streets)


# Поиск логина
@csrf_exempt
def find_login_to_terminal(request, username):
    if models.Clients.objects.filter(login=request.POST['login']).count() > 0:
        client = models.Clients.objects.get(login=request.POST['login'])
        client_info = {'tarif':client.select_tarif.price, 'balance':client.balance}
        return JsonResponse({'find_login':True, 'client_info':client_info})
    else:
        return JsonResponse({'find_login': False})


# Обновление пароля
def update_password(request, id):
    try:
        models.Employee.objects.get(id=request.user.id)
    except:
        return JsonResponse({'message':'Доступ запрещен'})
    json_new_password = {}

    client = models.Clients.objects.get(id=id)
    password = User.objects.make_random_password(length=9, allowed_chars='123456789')

    try:
        for device in client.select_clients_group.select_server.all():
            action_mikrotik = ActionMikroTik(device)
            action_mikrotik.update_password(client.login, password)
    except:
        json_new_password.update({'password':'Сервер не доступен', 'error':True})
    else:
        user = User.objects.get(id=client.user.id)
        user.set_password(password)
        user.save()
        json_new_password.update({'password': password})
        client.key = password
        client.save()

    return JsonResponse(json_new_password)


class CreateOrder(BaseAdminContentMixin, CreateView):
    method_to_view = 'add'
    model = models.Order
    fields = ['type_order', 'executor', 'client', 'description', 'framed', 'address']
    template_name = 'app_admin/create_order.html'
    success_url = '/'

    def get_success_url(self):
        self.success_url = '/'
        return super(CreateOrder, self).get_success_url()

    def form_valid(self, form):
        self.object = self.object = form.save(commit=False)
        self.object.creator = self.request.user.profile_employee
        super().form_valid(form)

        return redirect(reverse_lazy('pythonix_admin:order_info', kwargs={'pk':self.object.id}))


# Информация об ордере
class OrderInfoView(BaseAdminContentMixin, UpdateView):
    method_to_view = 'add'
    success_url = '/pythonix_admin/'
    model = models.Order
    context_object_name = 'order_info'
    template_name = 'app_admin/order_info.html'

    fields = ['type_order', 'executor', 'client', 'description', 'framed', 'address']


# Оптравка данных о клиенте монтажнику
def send_sms_info_client_ajax(request, id_client, id_employeer):
    try:
        models.Employee.objects.get(id=request.user.id)
    except:
        return JsonResponse({'message':'Доступ запрещен'})
    info_client = models.Clients.objects.get(id=id_client)
    info_employeer = models.Employee.objects.get(id=id_employeer)

    sms_messager = SMSC()
    text_message = '{} {} {} {}'.format(info_client.login, info_client.key, info_client.ip_address, info_client.mac_address)
    sms_messager.send_sms(info_employeer.mobile_phone, text_message)
    return JsonResponse({'message': 'Данные отправлены'})


# Пополнение счета через платежные системы
@csrf_exempt
def payment_from_pay_systems(request):
    print(request.POST)
    try:
        pay_system = models.PaySystemAccessData.objects.get(ip_access=request.META['REMOTE_ADDR'], token_access=request.POST.get('token'))
    except:
        return JsonResponse({'status': False, 'message': 'access error', 'action':request.POST.get('action')})


    if request.POST.get('action') == 'find_login':
        try:
            client = models.Clients.objects.get(login=request.POST['id_client'])
            return JsonResponse({'status': True, 'message': 'Login found', 'action': request.POST.get('action'), 'balance': client.balance})
        except:
            return JsonResponse({'status': False, 'message': 'Login not found', 'action': request.POST.get('action')})

    #if int(request.POST.get('transaction_number')) in list(pay_system.pay_system_transactions.values_list('transaction_number', flat=True)):
    #    return JsonResponse({'status': False, 'message': 'duplication transaction error', 'action':request.POST.get('action')})

    try:
        client = models.Clients.objects.get(login=request.POST['id_client'])

        new_balance = int(client.balance) + int(float(request.POST.get('sum')))

        models.PaySystemReportPay.objects.create(id_admin_select=pay_system, id_client_select=client, sum=int(float(request.POST.get('sum'))),
                                                 before_balance=client.balance, after_balance=new_balance, before_date_off=client.end_used_date)

        client.balance = int(client.balance) + int(float(request.POST.get('sum')))
        now_date = datetime.date.today()
        if client.end_used_date <= now_date and client.balance >= 0:
            if settings.TAKE_INFO_ACCOUNT_SETTINGS:
                if client.fix_work_period:
                    new_end_used_date = now_date.replace(day=1) + relativedelta(months=1)
                else:
                    new_end_used_date = now_date + relativedelta(months=1)
            else:
                if settings.WORK_PERIOD:
                    new_end_used_date = now_date.replace(day=1) + relativedelta(months=1)
                else:
                    new_end_used_date = now_date + relativedelta(months=1)
            client.internet_status = True
            client.end_used_date = new_end_used_date
        client.save()

        models.PySystemTransaction.objects.create(select_pay_system=pay_system, transaction_number=request.POST.get('transaction_number'),
                                                  login=request.POST.get('id_client'), sum=request.POST.get('sum'))

    except:
        return JsonResponse({'status': False, 'action': request.POST.get('action'), 'message': 'login not found error'})


    if client.balance >= 0:
        models.DeferredActionsWithClient.objects.create(client=client, action='on')

    #emails = [admin.admin.user.email for admin in models.SendEmailAdmin.objects.filter(event='payment')]
    #msg = EmailMessage('Pay client', '<p>Pay client {}</p>'.format(request.POST['id_client']),
    #                   settings.DEFAULT_FROM_EMAIL, emails)
    #msg.content_subtype = "html"
    #msg.send()

    return JsonResponse({'status': True, 'action': request.POST.get('action'), 'message': 'Pay ok', 'balance': client.balance})


# Получить PON данные клиента
def get_pon_info_client(request, id):
    try:
        request.user.profile_employee
    except:
        return JsonResponse({'message':'Вы не являетесь сотрудником'})

    client = models.Clients.objects.get(id=id)

    if client.onu_mac_address == None:
        return JsonResponse({'message': 'Укажите МАС адрес ONU', 'status':False})


    physical_networks = [physical_network.get('physical_network_id') for physical_network in client.select_clients_group.select_server.values()]
    pon_devices = models.SwitchingDevice.objects.filter(physical_network_id__in=physical_networks)

    if pon_devices.count() == 0:
        return JsonResponse({'message': 'PON устройства не найдены', 'status': False})

    onu_signal = False

    pon_info_client = {'message': '', 'status': True}

    for pon_device in pon_devices:
        pon_snmp = PonSNMP(pon_device.network_address, pon_device.snmp_public_community, '')
        onu_signal = pon_snmp.get_onu_signal(str(client.onu_mac_address)).get('onu_signal')
        if onu_signal != None:
            break

    pon_info_client = {'message': '', 'status': True, 'onu_signal':onu_signal}

    return JsonResponse(pon_info_client)