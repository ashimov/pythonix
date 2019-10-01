from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.contrib.auth.models import User
from django.conf import settings

import json
import requests

from pythonix_admin import models


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    # option_list = BaseCommand.option_list + (
    #    make_option('--market_place',
    #                help='Close all polls.'),
    # )


    def handle(self, *args, **options):
        clients_group_json = {2: 1, 1: 2}
        tarifs_json = {11: 11, 10:10, 9:9, 8:3, 7:4, 6:2, 5:1, 4:8, 3:7, 2:6, 1:5 }

        r = requests.get('http://stat2.kvazarlink.net/pythonix_admin/return_clients/')
        for client in r.json().get('clients'):
            try:
                user = User.objects.create_user(username=client.get('login'),
                                            email='{}@kvazarlink.net'.format(client.get('login')),
                                            password=client.get('password'))

                # client_group = models.ClientsGroups.objects.get(id=clients_group_json.get(client.get('select_clients_group')))
                # tarif = models.Tarifs.objects.get(id=tarifs_json.get(client.get('select_tarif')))
                models.Clients.objects.create(user=user, ip_address=client.get('ip_address'),
                                          select_tarif_id=client.get('select_tarif'),
                                          select_clients_group_id=client.get('select_clients_group'),
                                          create_date=client.get('create_date'),
                                          end_used_date=client.get('end_used_date'),
                                          deleted_user=client.get('deleted_user'),
                                          key=client.get('password'), login=client.get('login'),
                                              balance=client.get('balance'), internet_status=client.get('internet_status'))
            except:
                client_db = models.Clients.objects.get(login=client.get('login'))
                if int(client.get('balance')) < 0:
                    client_db.internet_status = False
                else:
                    client_db.internet_status = client.get('internet_status')
                client_db.balance=client.get('balance')
                client_db.select_clients_group_id = clients_group_json.get(client.get('select_clients_group'))
                client_db.select_tarif_id = tarifs_json.get(client.get('select_tarif'))
                client_db.save()

            print(client)
