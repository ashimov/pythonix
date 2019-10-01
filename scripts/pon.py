from easysnmp import Session
from easysnmp import exceptions


MIBS = {
    'onu_mac_addresses':'.1.3.6.1.4.1.3320.101.10.1.1.3',
    'onu_signal':'.1.3.6.1.4.1.3320.101.10.5.1.5.',
    'onu_distance':'1.3.6.1.4.1.3320.101.10.1.1.27',
    'all_onu_signal':'iso.3.6.1.4.1.3320.101.10.5.1.5'
}


class PonSNMP:
    def __init__(self, network_address, snmp_public_community, snmp_private_community):
        self.network_address = network_address
        self.snmp_public_community = snmp_public_community
        self.snmp_private_community = snmp_private_community
        self.session = Session(hostname=self.network_address, community=self.snmp_public_community, version=2)


    def send_email(self):
        print('SEND')


    def get_onu_signal(self, mac_address):

        try:
            onu_mac_address_items = self.session.walk(MIBS.get('onu_mac_addresses'))
            for item in onu_mac_address_items:
                print(item)
                if mac_address.lower() == ':'.join('{:02x}'.format(ord(x)) for x in item.value).lower():
                    onu_id = item.oid.split('.')[-1:][0]
                    mib_get_signal = '{}{}'.format(MIBS.get('onu_signal'), onu_id)
                    onu_signal = self.session.get(mib_get_signal)
                    return {'onu_signal': (float(onu_signal.value)*0.1)}
            return {'onu_signal': None}
        except exceptions.EasySNMPTimeoutError:
            return {'onu_signal': None}


    def get_all_onu_signal(self):
        all_onu_signal = []

        try:
            onu_mac_address_items = self.session.walk(MIBS.get('onu_mac_addresses'))
            print(onu_mac_address_items)
            for item in onu_mac_address_items:
                curent_onu_mac = ':'.join('{:02x}'.format(ord(x)) for x in item.value).lower()
                onu_id = item.oid.split('.')[-1:][0]
                mib_get_signal = '{}{}'.format(MIBS.get('onu_signal'), onu_id)
                onu_signal = self.session.get(mib_get_signal)
                if onu_signal.value != 'NOSUCHINSTANCE':
                    if int(onu_signal.value) < -260:
                        error_signal = True
                    else:
                        error_signal = False
                    all_onu_signal.append([curent_onu_mac, (float(onu_signal.value)*0.1), error_signal])
                else:
                    all_onu_signal.append([curent_onu_mac, 'ONU DOWN'])
            return all_onu_signal
        except exceptions.EasySNMPTimeoutError:
            return all_onu_signal


    def get_all_onu_distance(self):
        return [[item.oid.split('.')[-1:][0], item.value] for item in self.session.walk(MIBS.get('onu_distance'))]


    def get_all_onu_mac_address(self):
        return [[item.oid.split('.')[-1:][0], ':'.join('{:02x}'.format(ord(x)) for x in item.value).lower()] for item in self.session.walk(MIBS.get('onu_mac_addresses'))]


    def get_all_onu_signal(self):
        return [[item.oid.split('.')[-1:][0], item.value] for item in self.session.walk(MIBS.get('all_onu_signal'))]

    def get_all_onu_info(self):
        all_onu_info = {}

        all_onu_signal = self.get_all_onu_signal()
        all_onu_mac_address = self.get_all_onu_mac_address()
        all_onu_distance = self.get_all_onu_distance()

        [all_onu_info.update({item[0]: [item[1]]}) for item in all_onu_mac_address]

        [all_onu_info.get(item[0]).append(item[1]) for item in all_onu_distance]

        [all_onu_info.get(item[0]).append(item[1]) for item in all_onu_signal]

        return all_onu_info

