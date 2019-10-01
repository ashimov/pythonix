from django import forms

from captcha.fields import CaptchaField

from pythonix_admin import models


class DelClientForm(forms.Form):

    captcha = CaptchaField()


class CreateClientForm(forms.ModelForm):

    class Meta:
        model = models.Clients
        fields = ['select_clients_group', 'ip_address', 'ipv6_address', 'send_sms', 'select_tarif', 'select_street', 'mobile_phone',
                  'home_address', 'login', 'exemption', 'mac_address', 'onu_mac_address']

    def __init__(self, *args, **kwargs):
        super(CreateClientForm, self).__init__(*args, **kwargs)
        self.fields['ip_address'].required = True
        self.fields['select_tarif'].required = True
        self.fields['select_clients_group'].required = True
        self.fields['select_street'].required = True

        self.fields.keyOrder = [
            'select_clients_group', 'ip_address', 'ipv6_address', 'send_sms', 'select_tarif', 'select_street', 'mobile_phone',
                  'home_address', 'login', 'exemption', 'mac_address', 'onu_mac_address']
