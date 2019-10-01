__author__ = 'Jeka'
from django.views.generic import View, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import HttpResponseForbidden
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy

import datetime

from pythonix_admin import models


class BaseClientContentMixin(View):

    @method_decorator(login_required(login_url='/pythonix_client/client_login/'))
    def dispatch(self, request, *args, **kwargs):
        try:
            request.user.client
        except:
            if self.request.user.is_superuser == False:
                return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class ClientIndexPage(BaseClientContentMixin, DetailView):
    model = models.Clients
    template_name = 'app_client/index.html'

    def get(self, request, *args, **kwargs):
        self.kwargs.update({'pk':self.request.user.client.id})
        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientIndexPage, self).get_context_data(**kwargs)
        context['orders'] = models.Order.objects.filter(close=False, framed=True, client=self.request.user.client)
        return context


def my_login(request):
    ip_client = request.META['REMOTE_ADDR']
    clients = models.Clients.objects.filter(ip_address=ip_client)
    return render(request, 'app_client/my_login.html', {'clients':clients})


def client_login(request):
    if request.POST:
        user = authenticate(username=request.POST.get('login'), password=request.POST.get('password'))
        if user == None:
            return render(request, 'app_client/login.html', {})
        else:
            login(request, user)
            return redirect(reverse_lazy('pythonix_client:client_index'))
    return render(request, 'app_client/login.html', {})


def close_order(request):
    try:
        order = models.Order.objects.get(client=request.user.client, id=request.POST.get('id'))
        order.close = True
        order.note = request.POST.get('node')
        order.date_end = datetime.datetime.now()
        order.save()
    except:
        pass
    return redirect(reverse_lazy('pythonix_client:client_index'))