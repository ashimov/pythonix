from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from django.conf import settings
from django.core.urlresolvers import reverse

from scripts.pon import PonSNMP
from pythonix_admin import models

user_model = get_user_model()

class SectionCategoryBaseTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test',
                                        email='{}@{}'.format('test', 'inviteme.biz'),
                                        password='password', is_staff=True)

        physicalnetwork = models.PhysicalNetwork.objects.create(name='Home', abbreviation='home')

        tarif = models.Tarifs.objects.create(select_physicalnetwork=physicalnetwork, title='Unlim10', speed_up=10, speed_down=10,
                                             speed_up_unit='M', speed_down_unit='M', price=100, add_rule_in_device=False)

        ipv4networks = models.IPV4Networks.objects.create(ipv4networks='192.168.1.1', CIDR=24)
        server = models.Servers.objects.create(title='Home server', physical_network=physicalnetwork, network_address='192.168.1.1',
                                               login='ubnt', password='ubnt')

        street = models.Streets.objects.create(title='Home st', select_physical_network=physicalnetwork)

        clients_group = models.ClientsGroups.objects.create(title='Home Cable')
        clients_group.ipv4networks_list.add(ipv4networks)
        clients_group.select_server.add(server)
        clients_group.save()

        self.client = models.Clients.objects.create(user=user, ip_address='192.168.1.2', select_tarif=tarif,
                                      select_street=street, select_clients_group=clients_group, key='ubnt', onu_mac_address='A0:C6:EC:03:8C:42')


        self.pon_snmp = PonSNMP('192.168.200.101', 'public', '')


    def test_get_onu_signal(self):
        print(self.client.onu_mac_address.__str__().lower())
        #for client in models.Clients.objects.all():
        #    print(dir(client.onu_mac_address))

        print(self.pon_snmp.get_onu_signal(str(self.client.onu_mac_address)))