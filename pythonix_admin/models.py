from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

import datetime
from macaddress.fields import MACAddressField

from pythonix_admin import bl
from scripts.action_mikrotik import ActionMikroTik


# Сотрудники
class Employee(models.Model):
    ROLE_SUPER_ADMIN = 'ROLE_SUPER_ADMIN'
    ROLE_ADMIN = 'ROLE_ADMIN'
    ROLE_OPERATOR_PAYER = 'OPERATOR_PAYER'
    ROLE_OPERATOR = 'ROLE_OPERATOR'
    ROLE_INSTALLER = 'ROLE_INSTALLER'

    ROLE_METHODS = {
        ROLE_SUPER_ADMIN: ('show', 'add', 'delete', 'pay', 'log'),
        ROLE_ADMIN: ('show', 'add', 'delete', 'pay'),
        ROLE_OPERATOR_PAYER: ('show', 'pay'),
        ROLE_OPERATOR: ('show',),
        ROLE_INSTALLER: ('',)
    }

    ROLE_CHOICES = (
        (ROLE_SUPER_ADMIN, ROLE_SUPER_ADMIN),
        (ROLE_ADMIN, ROLE_ADMIN),
        (ROLE_OPERATOR_PAYER, ROLE_OPERATOR_PAYER),
        (ROLE_OPERATOR, ROLE_OPERATOR),
        (ROLE_INSTALLER, ROLE_INSTALLER),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='profile_employee')
    permissions_role = models.CharField(max_length=255, verbose_name='Выбор привелегий доступа',
                                        default=ROLE_OPERATOR, choices=ROLE_CHOICES)
    mobile_phone = models.CharField(max_length=13, validators=[bl.validate_phone], verbose_name='Номер телефона')


    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)


# Физическая сеть
class PhysicalNetwork(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название физической сети')
    select_admin = models.ManyToManyField(Employee, verbose_name='Выбор администратора', related_name='admins')
    abbreviation = models.CharField(max_length=150, verbose_name='Аббревиатура физической сети')
    channel_width = models.IntegerField(verbose_name='Ширина канала', blank=True, null=True)

    class Meta:
        verbose_name = 'Физическая сеть'
        verbose_name_plural = 'Физические сети'
        db_table = 'physical_network'

    def __str__(self):
        return '{}'.format(self.name)


# Сервера
class Servers(models.Model):
    SERVER_OS = (
        ('mikrotik', 'MikroTik RouterOS'),
    )

    title = models.CharField(max_length=150, verbose_name='Название Сервера')
    physical_network = models.ForeignKey(PhysicalNetwork, verbose_name='Выбор физической сети')
    device_type = models.CharField(max_length=255, verbose_name='Выбор операционной системы', default=1, choices=SERVER_OS)
    network_address = models.GenericIPAddressField(verbose_name='Сетевой адрес устройства')
    login = models.CharField(max_length=50, verbose_name='Логин для доступа к устройству')
    password = models.CharField(max_length=50, verbose_name='Пароль для доступа к устройству')
    api_port = models.IntegerField(verbose_name='API порт', default=8728)
    status_on_off = models.BooleanField(verbose_name='Состояние работы сервера', default=True)
    radius_used = models.BooleanField(default=False, verbose_name='Использование радиус сервера')

    class Meta:
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'
        db_table = 'device'

    def __str__(self):
        return '{}'.format(self.title)


# IP Подсети v4
class IPV4Networks(models.Model):
    MASK_CHOICES = tuple([(i, i) for i in range(1, 33)])
    ipv4networks = models.GenericIPAddressField(verbose_name='IP Подсети')
    CIDR = models.IntegerField(choices=MASK_CHOICES, default=24)
    ppp_auth = models.BooleanField(default=True, verbose_name='Использует PPP авторизацию')

    class Meta:
        verbose_name = "Подсеть IPv4"
        verbose_name_plural = 'Список подсетей IPv4'
        db_table = "ip_v4_networks"

    def __str__(self):
        return '{}'.format(self.ipv4networks)


# Группы клиентов
class ClientsGroups(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название группы')
    ipv4networks_list = models.ManyToManyField(IPV4Networks, verbose_name='Список подсетей IPv4', related_name='networks')
    select_admin = models.ManyToManyField(Employee, verbose_name='Выбор администратора', related_name='admin_clients_groups')
    select_server = models.ManyToManyField(Servers, verbose_name='Выбор сервера', related_name='servers')

    class Meta:
        verbose_name = 'Группа клиентов'
        verbose_name_plural = 'Группы клиентов'
        db_table = 'clients_groups'

    def __str__(self):
        return '{}'.format(self.title)


# Тарифы
class Tarifs(models.Model):
    UNIT_SPEED = (
    ('k', 'k'),('M', 'M'),
    )

    select_physicalnetwork = models.ForeignKey(PhysicalNetwork, verbose_name='Выбор физической сети')
    title = models.CharField(max_length=150, verbose_name='Название тарифа')
    speed_up = models.IntegerField(verbose_name='Исходящая скорость, значение')
    speed_down = models.IntegerField(verbose_name='Входящая скорость, значение')
    speed_up_unit = models.CharField(max_length=1, verbose_name='Исходящая скорость, единица измерения', choices=UNIT_SPEED)
    speed_down_unit = models.CharField(max_length=1, verbose_name='Входящая скорость, единица измерения', choices=UNIT_SPEED)
    price = models.IntegerField(verbose_name='Абонплата')
    speed_limit = models.BooleanField(verbose_name='Лимитирование скорости', default=False)
    limit_rule = models.CharField(max_length=200, verbose_name='Правило, лимита', blank=True, null=True,)
    add_rule_in_device = models.BooleanField(verbose_name='Создавать ли правила в устройстве', default=True)
    # Период работы клиентов с первого по первое True, с дня пополнения False
    fix_work_period = models.BooleanField(default=True, verbose_name='Работает с первого по первое')


    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if self.add_rule_in_device:
            try:
                for device in Servers.objects.filter(physical_network_id=self.select_physicalnetwork):
                    action_mikrotik = ActionMikroTik(device)
                    action_mikrotik.add_tarif(self.speed_up, self.speed_up_unit, self.speed_down, self.speed_down_unit)
                    return super().save(force_insert=False, force_update=False, using=None,
                            update_fields=None)
            except:
                return False
        else:
            return super().save(force_insert=False, force_update=False, using=None,
                                update_fields=None)

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        db_table = 'tarifs'

    def __str__(self):
        return '{} {}'.format(self.title, self.select_physicalnetwork.name)

# Улицы
class Streets(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название улицы')
    select_physical_network = models.ForeignKey(PhysicalNetwork, verbose_name='Выбор физической сети', related_name='streets')


    class Meta:
        verbose_name = 'Улицу'
        verbose_name_plural = 'Улицы'
        db_table = 'streets'

    def __str__(self):
        return '{} {}'.format(self.title, self.select_physical_network.name)


# Клиенты
class Clients(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='client')
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес клиена')
    ipv6_address = models.GenericIPAddressField(verbose_name='IPv6 адрес клиена', default="2001:0db8:11a3:09d7:1f34:8a2e:07a0:765d")
    send_sms = models.BooleanField(verbose_name='Желание получать смс', default=False)
    select_tarif = models.ForeignKey(Tarifs, verbose_name='Выбор тарифа')
    select_clients_group = models.ForeignKey(ClientsGroups, verbose_name='Выбор группы клиентов')
    create_date = models.DateField(verbose_name='Дата подключения', auto_now_add=True)
    end_used_date = models.DateField(verbose_name='Дата окончяния услуги', default=(datetime.datetime.now() + datetime.timedelta(days=settings.NEW_CLIENT_DAYS)))
    select_street = models.ForeignKey(Streets, verbose_name='Выбор улицы', blank=True, null=True)
    mobile_phone = models.CharField(max_length=50, verbose_name='Мобильный телефон', blank=True, null=True,)
    home_address = models.CharField(max_length=50, verbose_name='Домашний адрес', blank=True, null=True,)
    network_traffic_per_day = models.IntegerField(verbose_name='Сетевой трафик за день', null=True, default=0)
    network_traffic_for_the_month = models.IntegerField(verbose_name='Сетевой трафик за месяц', null=True, default=0)
    balance = models.IntegerField(verbose_name='Баланс', default=0)
    internet_status = models.BooleanField(verbose_name='Статус клиента, доступ разрешен/запрещен', default=True)
    error_card = models.IntegerField(verbose_name='Ошибки пополнения карточкой', null=True, default=0)
    deleted_user = models.BooleanField(default=False, verbose_name='Статус удаления пользователя')
    key = models.CharField(max_length=50)
    login = models.CharField(max_length=50, verbose_name='Логин', default='')
    exemption = models.BooleanField(default=False)
    # Период работы клиентов с первого по первое True, с дня пополнения False
    fix_work_period = models.BooleanField(default=False, verbose_name='Работает с первого по первое')
    vk = models.CharField(max_length=255, verbose_name='Профиль Вконтакте', default='', blank=True, null=True)
    facebook = models.CharField(max_length=255, verbose_name='Профиль в facebook', default='', blank=True, null=True)
    mac_address = MACAddressField(null=True, blank=True, integer=False, verbose_name='МАС адрес клиента')
    onu_mac_address = MACAddressField(null=True, blank=True, integer=False, verbose_name='МАС адрес ONU')

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        db_table = "clients"

    def __str__(self):
        return '{} {} {} {}'.format(self.login, self.select_clients_group, self.ip_address, self.deleted_user)


# Временные платежи
class TemporaryPay(models.Model):
    del_pay = models.DateField(verbose_name='Дата удаления временного платежа',
                                     default=(datetime.datetime.now() + datetime.timedelta(days=settings.TEMPORARY_PAY_COUNT_DAYS)))
    user = models.ForeignKey(Clients)
    price = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Временный платеж"
        verbose_name_plural = "Временные платежи"

    def __str__(self):
        return '{} {}'.format(self.del_pay, self.user)


# Отчет пополнений клиентов
class ReportPayAdmin(models.Model):
    id_admin_select = models.ForeignKey(Employee, verbose_name='Выбор Администратора')
    id_client_select = models.ForeignKey(Clients, verbose_name='Выбор Клиента')
    sum = models.IntegerField(verbose_name='Сумма пополнения')
    date_of_refill = models.DateField(verbose_name='Дата пополнения', auto_now_add=True)
    before_balance = models.CharField(max_length=255, verbose_name='Баланс до', default='')
    after_balance = models.CharField(max_length=255, verbose_name='Баланс после', default='')
    before_date_off = models.CharField(max_length=255, verbose_name='Дата отключения до пополнения', default='')
    note = models.CharField(max_length=255, verbose_name='Примечание', default='')

    class Meta:
        verbose_name = "Пополнение администратором"
        verbose_name_plural = "Пополнение администратором"
        db_table = "report_pay_admin"

    def __str__(self):
        return '{} {} {} {} {} {} {} '.format(self.id_admin_select, self.id_client_select, self.sum, self.date_of_refill,
                                               self.before_balance, self.after_balance, self.before_date_off)


# Список администраторов для Email уведомлений
class SendEmailAdmin(models.Model):
    EVENTS = (
        ('new_month', 'new_month'),
        ('clients_off', 'clients_off'),
        ('celery_on', 'celery_on'),
        ('payment', 'payment'),
        ('deferred_actions', 'Отложенные действия')
    )
    event = models.CharField(max_length=255, choices=EVENTS)
    admin = models.ForeignKey(Employee, related_name='sending_emails')

    class Meta:
        verbose_name = "Администратор подписаный на уведомления"
        verbose_name_plural = "Администраторы подписаные на уведомления"

    def __str__(self):
        return '{} {}'.format(self.event, self.admin.user.username)


# Отчета перехода на новый месяц
class ReportNewMonth(models.Model):
    client_select = models.ForeignKey(Clients, verbose_name='Выбор Клиента')
    date_of_refill = models.DateField(verbose_name='Дата пополнения', auto_now_add=True)
    before_balance = models.CharField(max_length=255, verbose_name='Баланс до')
    after_balance = models.CharField(max_length=255, verbose_name='Баланс после')
    before_date_off = models.CharField(max_length=255, verbose_name='Дата отключения до пополнения')

    class Meta:
        verbose_name = "Переход на новый месяц"
        verbose_name_plural = "Переход на новый месяц"
        db_table = "report_new_month"

    def __str__(self):
        return '{} {} {} {} {}'.format(self.client_select, self.date_of_refill,
                                               self.before_balance, self.after_balance, self.before_date_off)


# Логи платежей
class LogPay(models.Model):
    id_admin_select = models.ForeignKey(Employee, verbose_name='Выбор Администратора')
    id_client_select = models.ForeignKey(Clients, verbose_name='Выбор Клиента')
    sum = models.IntegerField(verbose_name='Сумма пополнения')
    date_of_refill = models.DateField(verbose_name='Дата пополнения', auto_now_add=True)
    before_balance = models.CharField(max_length=255, verbose_name='Баланс до')
    before_date_off = models.CharField(max_length=255, verbose_name='Дата отключения до пополнения')

    class Meta:
        verbose_name = "Лог пополнения"
        verbose_name_plural = "Логи пополнений"

    def __str__(self):
        return '{} {}'.format(self.client_select, self.date_of_refill)


# Заявки
class Order(models.Model):
    CONNECTION = 'CONNECTION'
    REPAIRS = 'REPAIRS'

    ORDER_TYPES = (
        (REPAIRS, 'Ремонт'),
        (CONNECTION, 'Подключение')
    )

    ORDER_TYPES_DICT = {
        CONNECTION: 'Подключение',
        REPAIRS: 'Ремонт'
    }

    type_order = models.CharField(max_length=255, verbose_name='Тип заявки',
                                        default=CONNECTION, choices=ORDER_TYPES)
    creator = models.ForeignKey(Employee, related_name='creator_emploee', verbose_name='Оформитель ордера')
    executor = models.ForeignKey(Employee, related_name='executor_emploee', verbose_name='Исполнитель ордера')
    client = models.ForeignKey(Clients, related_name='orders_client', verbose_name='Выбор клиента')
    date_created = models.DateTimeField(verbose_name='Дата создания заявки', auto_now_add=True)
    date_end = models.DateField(verbose_name='Дата выполнения заявки', null=True, default=None, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес ордера')
    description = models.TextField(verbose_name='Описание', default='')
    note = models.TextField(verbose_name='Примечания', default='')
    framed = models.BooleanField(default=False, verbose_name='Оформленный')
    close = models.BooleanField(default=False, verbose_name='Закрыт')

    def get_type_order(self):
        return self.ORDER_TYPES_DICT.get(self.type_order)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return '{} {}'.format(self.creator, self.client.login)


# Системные события
class SystemEvent(models.Model):
    CONNECT_DEVICE_ERROR = 'CONNECT_ERROR'

    EVENT_TYPES = (
        (CONNECT_DEVICE_ERROR, 'Ошибка соединения с устройством'),
    )

    IMPORTANCE_TYPES = (
        ('HIGH', 'Высокая'),
        ('MEDIUM', 'Средняя'),
        ('LOW', 'Низкая')
    )


# Данные доступа платежных систем
class PaySystemAccessData(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название платежной системы')
    ip_access = models.GenericIPAddressField(verbose_name='Разрешенные IP')
    token_access = models.CharField(max_length=255, verbose_name='Токен доступа')

    class Meta:
        verbose_name = "Платежная система"
        verbose_name_plural = "Платежные системы"

    def __str__(self):
        return '{} {} {}'.format(self.title, self.ip_access, self.token_access)


# Транзакции от платежных систем
class PySystemTransaction(models.Model):
    select_pay_system = models.ForeignKey(PaySystemAccessData, related_name='pay_system_transactions', verbose_name='Платежная система')
    transaction_number = models.IntegerField(verbose_name='Номер транзакции')
    transaction_date = models.DateField(auto_now_add=True, verbose_name='Номер транзакции')
    transaction_time = models.DateTimeField(auto_now_add=True, verbose_name='Время транзакции')
    login = models.CharField(max_length=255, default='', verbose_name='логин')
    sum = models.CharField(max_length=255, default='', verbose_name='Сумма транзакции')

    class Meta:
        verbose_name = "Транзакция платежной системы"
        verbose_name_plural = "Транзакции платежной системы"

    def __str__(self):
        return '{} {} {} {} {}'.format(self.select_pay_system.title, self.transaction_number, self.transaction_date, self.login, self.sum)


# Отчет пополнений клиентов платежными системами
class PaySystemReportPay(models.Model):
    id_admin_select = models.ForeignKey(PaySystemAccessData, verbose_name='Выбор платежной системы', related_name='pay_system_report_pays')
    id_client_select = models.ForeignKey(Clients, verbose_name='Выбор Клиента')
    sum = models.IntegerField(verbose_name='Сумма пополнения')
    date_of_refill = models.DateField(verbose_name='Дата пополнения', auto_now_add=True)
    time_of_refill = models.TimeField(verbose_name='Время пополнения', auto_now_add=True)
    before_balance = models.CharField(max_length=255, verbose_name='Баланс до', default='')
    after_balance = models.CharField(max_length=255, verbose_name='Баланс после', default='')
    before_date_off = models.CharField(max_length=255, verbose_name='Дата отключения до пополнения', default='')

    class Meta:
        verbose_name = "Пополнение платежной системой"
        verbose_name_plural = "Пополнения платежными системами"
        db_table = "report_pay_pay_systems"

    def __str__(self):
        return '{} {} {} {} {} {} {} {}'.format(self.id_admin_select, self.id_client_select, self.sum, self.date_of_refill,
                                               self.time_of_refill, self.before_balance, self.after_balance, self.before_date_off)


# Отложенные действия с клиентами
class DeferredActionsWithClient(models.Model):
    ACTIONS = (
        ('off', 'Отключить'),
        ('on', 'Включить'),
        ('create', 'Создать'),
        ('del', 'Удалить'),
    )
    action = models.CharField(max_length=255, choices=ACTIONS)
    client = models.ForeignKey(Clients)
    create_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    scheduled_implementation_date = models.DateField(null=True, blank=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Отложенное действие с клиентом"
        verbose_name_plural = "Отложенные действия с клиентами"

    def __str__(self):
        return '{}'.format(self.client.login)


# Коммутационные устройства
class SwitchingDevice(models.Model):
    DEVICE_TYPES = (
        ('bdcom', 'BDCOM'),
    )

    title = models.CharField(max_length=250, verbose_name='Название устройства')
    physical_network = models.ForeignKey(PhysicalNetwork, verbose_name='Выбор физической сети', related_name='switching_devices')
    device_type = models.CharField(max_length=255, verbose_name='Выбор типа устройства', default=1, choices=DEVICE_TYPES)
    network_address = models.GenericIPAddressField(verbose_name='Сетевой адрес устройства')
    login = models.CharField(max_length=50, verbose_name='Логин для доступа к устройству', null=True, blank=True)
    password = models.CharField(max_length=50, verbose_name='Пароль для доступа к устройству', null=True, blank=True)
    api_port = models.IntegerField(verbose_name='API порт', null=True, blank=True)
    status_on_off = models.BooleanField(verbose_name='Состояние работы устройства', default=True)
    radius_used = models.BooleanField(default=False, verbose_name='Использование радиус сервера')
    snmp_public_community = models.CharField(max_length=255, verbose_name='Публичное сообщество SNMP')
    snmp_private_community = models.CharField(max_length=255, verbose_name='Приватное сообщество SNMP', null=True, blank=True)
    telnet_port = models.IntegerField(verbose_name='Telnet порт', null=True, blank=True)
    ssh_port = models.IntegerField(verbose_name='SSH порт', null=True, blank=True)
    max_numbers_onu_to_port = models.PositiveIntegerField(verbose_name='Максимальное колличество ONU на порт', null=True, blank=True)

    class Meta:
        verbose_name = 'Коммутационное устройство'
        verbose_name_plural = 'Коммутационные устройства'
        db_table = 'switching_device'

    def __str__(self):
        return '{}'.format(self.title)
