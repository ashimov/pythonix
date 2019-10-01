from celery.task import task
import datetime
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.core import management
from django.core.mail import EmailMessage

import logging

from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from pythonix4.celery import app

from pythonix_admin import models
from pythonix_admin import bl
from scripts.action_mikrotik import ActionMikroTik


def deferred_actions_text_messages(action_name, info, status):
    return '{} {} {}'.format(action_name, info, status)


@task
def new_month():
    new_month_clients = ' '
    no_money_clients = ' '



    emails = [admin.admin.user.email for admin in models.SendEmailAdmin.objects.filter(event='new_month')]

    #msg = EmailMessage('Backup DB', '<p>Backup DB</p>', settings.DEFAULT_FROM_EMAIL, emails)
    #msg.content_subtype = "html"
    #msg.attach_file(settings.BACKUP_DIR+'/backup_postgresql.sql')
    #msg.send()

    #management.call_command('dbbackup')

    for client in models.Clients.objects.filter(end_used_date__lte=datetime.date.today(), balance__gte=0, deleted_user=False, exemption=False):

        before_balance = client.balance

        client.balance -= client.select_tarif.price

        now_date = datetime.date.today()

        if client.balance < 0:
            client.internet_status = False
            no_money_clients += ' ' + client.login
        else:

            models.ReportNewMonth.objects.create(client_select=client, date_of_refill=now_date, before_balance=before_balance,
                                                 after_balance=client.balance, before_date_off=client.end_used_date)

            if client.fix_work_period:
                if client.fix_work_period:
                    new_end_used_date = now_date.replace(day=1) + relativedelta(months=1)
                else:
                    new_end_used_date = now_date + relativedelta(months=1)
            else:
                if client.select_tarif.fix_work_period:
                    new_end_used_date = now_date.replace(day=1) + relativedelta(months=1)
                else:
                    new_end_used_date = now_date + relativedelta(months=1)

            client.end_used_date = new_end_used_date
            client.internet_status = True
            new_month_clients += ' ' + client.login
        client.save()


    bl.send_email(emails, 'app_admin/email_templates/new_month.html', 'Новый Месяц',
                  date=datetime.date.today(), new_month_clients=new_month_clients, no_money_clients=no_money_clients)
    return 'new_month'


@task
def clients_off():
    off_clients = ' '
    emails = [admin.admin.user.email for admin in models.SendEmailAdmin.objects.filter(event='clients_off')]
    for client in models.Clients.objects.filter(internet_status=False, deleted_user=False, exemption=False):
        off_clients += ' ' + client.login
        for device in client.select_clients_group.select_server.all():
            try:
                action_mikrotik = ActionMikroTik(device)
                action_mikrotik.off_client(client.ip_address)
            except:
                bl.send_email(emails, 'app_admin/email_templates/server_is_not_available.html', 'Новый Месяц Client OFF',
                              date=datetime.date.today(), server_title=device.title)


    bl.send_email(emails, 'app_admin/email_templates/new_month_client_off.html', 'Новый Месяц Client OFF',
                  date=datetime.date.today(), off_clients=off_clients)


@app.task
def celery_on():
    off_clients = ' '
    emails = [admin.admin.user.email for admin in models.SendEmailAdmin.objects.filter(event='celery_on')]

    bl.send_email(emails, 'app_admin/email_templates/new_month_client_off.html', 'celery work',
                  date=datetime.date.today(), off_clients=off_clients)


@task
def deferred_actions_with_customers():
    ('off', 'Отключить'),
    ('on', 'Включить'),
    ('del', 'Удалить'),
    ('create', 'Создать'),
    ('del', 'Удалить'),
    for action in models.DeferredActionsWithClient.objects.filter(status=False, scheduled_implementation_date__isnull=True):
        print(action.id, action.scheduled_implementation_date)

        for device in action.client.select_clients_group.select_server.all():

            if action.action == 'create':
                try:
                    action_mikrotik = ActionMikroTik(device)
                    action_mikrotik.create_user(action.client.login, action.client.key, action.client.ip_address, action.client.select_tarif)
                    action.status = True
                    action.save()

                    emails = [admin.admin.user.email for admin in
                              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions',
                    #                   deferred_actions_text_messages(action.action, action.client.login, 'work'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()

                except:
                    emails = [admin.admin.user.email for admin in models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions', deferred_actions_text_messages(action.action, action.client.login, 'error'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()

            if action.action == 'on':
                try:
                    action_mikrotik = ActionMikroTik(device)
                    action_mikrotik.on_client(action.client.ip_address)
                    action.status = True
                    action.save()

                    emails = [admin.admin.user.email for admin in
                              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions',
                    #                   deferred_actions_text_messages(action.action, action.client.login, 'work'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()
                except:
                    emails = [admin.admin.user.email for admin in
                              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions',
                    #                   deferred_actions_text_messages(action.action, action.client.login, 'error'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()

            if action.action == 'off':
                try:
                    action_mikrotik = ActionMikroTik(device)
                    action_mikrotik.off_client(action.client.ip_address)
                    action.status = True
                    action.save()

                    emails = [admin.admin.user.email for admin in
                              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions',
                    #                   deferred_actions_text_messages(action.action, action.client.login, 'worm'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()
                except:
                    emails = [admin.admin.user.email for admin in
                              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions',
                    #                   deferred_actions_text_messages(action.action, action.client.login, 'error'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()

            if action.action == 'del':
                try:
                    action_mikrotik = ActionMikroTik(device)
                    action_mikrotik.delete_user(action.client.login, action.client.ip_address)
                    action.status = True
                    action.save()

                    emails = [admin.admin.user.email for admin in
                              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions',
                    #                   deferred_actions_text_messages(action.action, action.client.login, 'work'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()
                except:
                    emails = [admin.admin.user.email for admin in
                              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
                    #msg = EmailMessage('deferred_actions',
                    #                   deferred_actions_text_messages(action.action, action.client.login, 'error'),
                    #                   settings.DEFAULT_FROM_EMAIL, emails)
                    #msg.content_subtype = "html"
                    #msg.send()


