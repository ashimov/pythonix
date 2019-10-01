from django.contrib import admin

from pythonix_admin import models


class ClientAdmin(admin.ModelAdmin):
    model = models.Clients
    search_fields = ['login', 'ip_address']
    list_display = ('login', 'ip_address', 'select_tarif', 'select_clients_group', 'end_used_date',
                    'balance', 'internet_status')

    list_filter = ('select_tarif', 'select_clients_group', 'end_used_date',
                    'balance', 'internet_status')


class ReportPayAdminAdmin(admin.ModelAdmin):
    model = models.ReportPayAdmin
    fields = ('id_admin_select', 'id_client_select', 'sum', 'date_of_refill', 'before_balance',
              'after_balance', 'before_date_off')

    list_display = ('id_admin_select', 'id_client_select', 'sum', 'date_of_refill', 'before_balance',
              'after_balance', 'before_date_off')

    list_filter = ('id_admin_select', 'id_client_select', 'date_of_refill')


class ReportNewMonthAdmin(admin.ModelAdmin):
    list_display = ('client_select', 'date_of_refill', 'before_balance', 'after_balance', 'before_date_off')


class LogPayAdminAdmin(admin.ModelAdmin):
    model = models.LogPay
    fields = ('id_admin_select', 'id_client_select', 'sum', 'date_of_refill', 'before_balance', 'before_date_off')

    list_display = ('id_admin_select', 'id_client_select', 'sum', 'date_of_refill', 'before_balance', 'before_date_off')

    list_filter = ('id_admin_select', 'id_client_select', 'date_of_refill')


class OrderAdmin(admin.ModelAdmin):
    model = models.Order

    list_display = ('type_order', 'creator', 'executor', 'client', 'date_created', 'date_end', 'close')


class PaySystemTransactionAdmin(admin.ModelAdmin):
    model = models.PySystemTransaction
    list_display = ('select_pay_system', 'transaction_number', 'transaction_date', 'login', 'sum')
    readonly_fields = ('transaction_number', 'transaction_date', 'login', 'sum')


class PaySystemReportPayAdmin(admin.ModelAdmin):
    model = models.PaySystemReportPay
    fields = ('id_admin_select', 'id_client_select', 'sum', 'date_of_refill', 'time_of_refill', 'before_balance', 'after_balance', 'before_date_off')

    list_display = ('id_admin_select', 'id_client_select', 'sum', 'date_of_refill', 'before_balance', 'after_balance', 'before_date_off')

    list_filter = ('id_admin_select', 'id_client_select', 'date_of_refill')


class DeferredActionsWithClientAdmin(admin.ModelAdmin):
    model = models.DeferredActionsWithClient

    list_display = ('action', 'client', 'create_date', 'update_date', 'scheduled_implementation_date','status')


admin.site.register(models.Employee)
admin.site.register(models.ClientsGroups)
admin.site.register(models.IPV4Networks)
admin.site.register(models.PhysicalNetwork)
admin.site.register(models.Servers)
admin.site.register(models.Clients, ClientAdmin)
admin.site.register(models.Tarifs)
admin.site.register(models.Streets)
admin.site.register(models.ReportPayAdmin, ReportPayAdminAdmin)
admin.site.register(models.TemporaryPay)
admin.site.register(models.SendEmailAdmin)
admin.site.register(models.ReportNewMonth, ReportNewMonthAdmin)
admin.site.register(models.LogPay, LogPayAdminAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.PaySystemAccessData)
admin.site.register(models.PySystemTransaction, PaySystemTransactionAdmin)
admin.site.register(models.PaySystemReportPay, PaySystemReportPayAdmin)
admin.site.register(models.DeferredActionsWithClient, DeferredActionsWithClientAdmin)
admin.site.register(models.SwitchingDevice)
