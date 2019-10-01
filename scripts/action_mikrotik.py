import socket

from scripts.RosAPI import ApiRos

class ActionMikroTik:
    def __init__(self, device):
        self.device = device
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((device.network_address, device.api_port))
        self.apiros = ApiRos(s);
        self.apiros.login(device.login, device.password)

    def create_user(self, login, password, ip_client, tariff):
        self.apiros.talk(["/ppp/secret/add", "=name=" + login, "=password=" + password, "=remote-address=" + ip_client,
                           "=profile=" + str(tariff.speed_up) + tariff.speed_up_unit + str(tariff.speed_down) + tariff.speed_down_unit])
        self.apiros.talk(["/ip/firewall/address-list/add", "=address=" + ip_client, "=list=" + "internet", ])

    def delete_user(self, login, ip_address):
        for record in self.apiros.talk(["/ppp/secret/print", "=.proplist=" + ".id,name", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=name'] == login:
                    self.apiros.talk(["/ppp/secret/remove", "=.id=" + record[1]['=.id'],])


        for record in self.apiros.talk(["/ip/firewall/address-list/print", "=.proplist="+".id,address",]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=address'] == ip_address:
                    self.apiros.talk(["/ip/firewall/address-list/remove", "=.id=" + record[1]['=.id'],])

    # Обновление IP адреса
    def update_ip(self, login, old_ip, new_ip):
        for record in self.apiros.talk(["/ppp/secret/print", "=.proplist=" + ".id,name", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=name'] == login:
                    self.apiros.talk(["/ppp/secret/set", "=remote-address=" + new_ip, "=.id=" + record[1]['=.id'],])


        for record in self.apiros.talk(["/ip/firewall/address-list/print", "=.proplist="+".id,address",]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=address'] == old_ip:
                    self.apiros.talk(["/ip/firewall/address-list/set", "=address=" + new_ip, "=.id=" + record[1]['=.id'],])

    # Обновить логин
    def update_login(self, old_login, new_login):
        for record in self.apiros.talk(["/ppp/secret/print", "=.proplist=" + ".id,name", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=name'] == old_login:
                    self.apiros.talk(["/ppp/secret/set", "=name=" + new_login, "=.id=" + record[1]['=.id'],])

    # Включение клиента
    def on_client(self, ip):
        for record in self.apiros.talk(["/ip/firewall/address-list/print", "=.proplist=" + ".id,address", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=address'] == ip:
                    self.apiros.talk(["/ip/firewall/address-list/enable", "=.id=" + record[1]['=.id'],])

    # Отключение клиента
    def off_client(self, ip):
        for record in self.apiros.talk(["/ip/firewall/address-list/print", "=.proplist=" + ".id,address", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=address'] == ip:
                    self.apiros.talk(["/ip/firewall/address-list/disable", "=.id=" + record[1]['=.id'], ])

    # Поиск в ARP таблице
    def get_arp(self, ip):
        for record in self.apiros.talk(["/ip/arp/print", "=.proplist=" + ".id,address", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=address'] == ip:
                    return True
        return False

    # Поиск в PPP active
    def get_ppp(self, login):
        for record in self.apiros.talk(["/ppp/active/print", "=.proplist=" + ".id,name,uptime", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=name'] == login:
                    return record[1]['=uptime']
        return False

    # Обновление тарифа
    def update_tariff(self, login, tariff):
        for record in self.apiros.talk(["/ppp/secret/print", "=.proplist=" + ".id,name", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=name'] == login:
                    self.apiros.talk(["/ppp/secret/set", "=profile=" + str(tariff.speed_up) + tariff.speed_up_unit + str(tariff.speed_down) + tariff.speed_down_unit, "=.id=" + record[1]['=.id'], ])
                    return True
        return False

    # Добавить тариф
    def add_tarif(self, speed_up, speed_up_unit, speed_down, speed_down_unit):
        self.apiros.talk(
            ["/ppp/profile/add", "=name=" + str(speed_up) + speed_up_unit + str(speed_down) + speed_down_unit,
             "=rate-limit=" + str(speed_up) + speed_up_unit + '/' + str(speed_down) + speed_down_unit,])


    # Получить список PPP Active
    def get_ppp_active(self):
        ppp_active = {}
        for record in self.apiros.talk(["/ppp/active/print", "=.proplist=" + ".id,name,uptime", ]):
            if record[1] == {}:
                pass
            else:
                ppp_active.update({record[1]['=name']: record[1]['=uptime']})
        return ppp_active

    # Обновить пароль
    def update_password(self, login, password):
        for record in self.apiros.talk(["/ppp/secret/print", "=.proplist=" + ".id,name", ]):
            if record[1] == {}:
                pass
            else:
                if record[1]['=name'] == login:
                    self.apiros.talk(["/ppp/secret/set", "=password=" + password, "=.id=" + record[1]['=.id'], ])


