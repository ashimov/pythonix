from django.core.mail import EmailMessage
from django.template import loader
from django.conf import settings
from django.core.validators import ValidationError
from django.contrib.auth.hashers import get_hasher
from django.utils.crypto import get_random_string

import phonenumbers
from dateutil.relativedelta import relativedelta
import datetime

from scripts.action_mikrotik import ActionMikroTik
from pythonix_admin import models


def validate_phone(phone):
    result = phonenumbers.parse(phone, None)

    if len(phone) < 13 or result.country_code != 380:
        raise ValidationError('{} не верный формат телефона'.format(phone))


def send_html_creator(html_path):
    return loader.get_template(html_path).template.source


def send_email(emails, html, EMAIL_SUBJECT, **kwargs):
    html = send_html_creator(html).format(**kwargs)
    msg = EmailMessage(EMAIL_SUBJECT, html, settings.DEFAULT_FROM_EMAIL, emails)
    msg.content_subtype = "html"
    msg.send()


# Пополнение счета
def pay_balance(client, admin, sum, temporary_pay, temporary_pay_model, report_pay_admin_model):
    json_balance = {}

    before_balance = client.balance

    client.balance = int(client.balance) + int(sum)

    old_end_used_date = client.end_used_date

    if (int(client.balance)  >= 0):
        try:
            for device in client.select_clients_group.select_server.all():
                action_mikrotik = ActionMikroTik(device)
                action_mikrotik.on_client(client.ip_address)
                json_balance.update({'message':'Счет пополнен'})
        except:
            json_balance.update({'message':'Сервер не доступен'})
        else:
            client.internet_status = True

            now_date = datetime.date.today()
            if client.end_used_date <= now_date:

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
            client.save()

    else:
        json_balance.update({'message':'Недостаточно средств'})
        client.save()

    if int(temporary_pay) == 1:
        temporary_pay_model.objects.create(user=client, price=int(sum))
    # Добавляем запись в отчет о пополнениях
    report_pay_admin_model.objects.create(id_admin_select=admin.profile_employee, id_client_select=client, sum=sum,
                                         before_balance=before_balance, after_balance=client.balance, before_date_off=old_end_used_date)

    json_balance.update({'balance':client.balance})
    return json_balance


# Пополнение счета NEW
def pay_balance_new(client, admin, sum, temporary_pay, temporary_pay_model, report_pay_admin_model):
    json_balance = {}

    before_balance = client.balance

    client.balance = int(client.balance) + int(sum)

    old_end_used_date = client.end_used_date

    if (int(client.balance)  >= 0):
        models.DeferredActionsWithClient.objects.create(client=client, action='on')

        client.internet_status = True

        now_date = datetime.date.today()
        if client.end_used_date <= now_date:

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
        client.save()
    else:
        json_balance.update({'message':'Недостаточно средств'})
        client.internet_status = False
        client.save()

    if int(temporary_pay) == 1:
        temporary_pay_model.objects.create(user=client, price=int(sum))
    # Добавляем запись в отчет о пополнениях
    report_pay_admin_model.objects.create(id_admin_select=admin.profile_employee, id_client_select=client, sum=sum,
                                         before_balance=before_balance, after_balance=client.balance, before_date_off=old_end_used_date)

    emails = [admin.admin.user.email for admin in
              models.SendEmailAdmin.objects.filter(event='deferred_actions')]
    msg = EmailMessage('Пополнение счета администратором', '<p>Администратор {}</p><p>Клиент {} сумма {} баланс до {}  баланс после {}</p>'.format(admin,  client.login, sum, before_balance, client.balance),
                       settings.DEFAULT_FROM_EMAIL, emails)
    msg.content_subtype = "html"
    #msg.send()

    json_balance.update({'balance':client.balance})
    return json_balance

