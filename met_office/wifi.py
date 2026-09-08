import binascii
import network
import requests as r
import ujson as json
import time


class WiFiStatus:
    WrongPassword = -3
    NoAccessPointFound = -2
    ConnectFail = -1
    Idle = 0
    Connecting = 1
    GotIP = 3

    _values = [WrongPassword, NoAccessPointFound,
               ConnectFail, Idle, Connecting, GotIP]

    def __init__(self, name: str, value: int) -> None:
        self._name = name
        self._value = value

        self.WrongPassword = WiFiStatus.WrongPassword
        self.NoAccessPointFound = WiFiStatus.NoAccessPointFound
        self.ConnectFail = WiFiStatus.ConnectFail
        self.Idle = WiFiStatus.Idle
        self.Connecting = WiFiStatus.Connecting
        self.GotIP = WiFiStatus.GotIP

    @staticmethod
    def __call__(value: int):
        return WiFiStatus._match(value)

    def __repr__(self) -> str:
        return f'WiFiStatus.{self._name}'

    @property
    def Failed(self) -> bool:
        return self._value in [WiFiStatus.WrongPassword, WiFiStatus.NoAccessPointFound, WiFiStatus.ConnectFail] or self._value < 0 or self._value > 3

    @staticmethod
    def InvalidStatus(status: int) -> bool:
        return status not in WiFiStatus._values

    @staticmethod
    def _match(value: int) -> WiFiStatus:
        if value == WiFiStatus.WrongPassword:
            name = 'WrongPassword'
        elif value == WiFiStatus.NoAccessPointFound:
            name = 'NoAccessPointFound'
        elif value == WiFiStatus.ConnectFail:
            name = 'ConnectFail'
        elif value == WiFiStatus.Idle:
            name = 'Idle'
        elif value == WiFiStatus.Connecting:
            name = 'Connecting'
        elif value == WiFiStatus.GotIP:
            name = 'GotIP'
        else:
            raise AttributeError(
                f'value {value} is not recognised for WiFiStatus')

        return WiFiStatus(name, value)

    @property
    def Success(self) -> bool:
        return self._value >= WiFiStatus.GotIP


class CouldNotConnectError(Exception):
    def __init__(self, *args: object) -> None:
        Exception.__init__(self, *args)


class WiFiNetwork:
    def __init__(self, wlan, ssid: str, bssid: str, channel: int, rssi: int, security: int, hidden: int) -> None:
        """
        WiFi: (ssid, bssid, channel, RSSI, security, hidden)

        Possible security values (see https://docs.micropython.org/en/latest/library/network.WLAN.html):
            0 – open
            1 – WEP
            2 – WPA-PSK
            3 – WPA2-PSK
            4 – WPA/WPA2-PSK

        Possible hidden values:
            0 – visible
            1 – hidden
        """
        self._wlan = wlan

        self._ssid: str = ssid
        self._bssid: str = bssid
        self._channel: int = channel
        self._rssi: int = rssi
        self._security: int = security
        self._hidden: int = hidden

        self._password: str = ""

    def __repr__(self) -> str:
        return '{' + f'ssid: {self.ssid}, bssid: {self.bssid}, channel: {self.channel}, rssi: {self.rssi}, security: {self.security}, hidden: {self.hidden}'+'}'

    @classmethod
    def from_tuple(cls, wlan, specs: tuple[bytes, bytes, int, int, int, int]):
        ssid_raw: bytes = specs[0]
        ssid_raw_str: str = str(ssid_raw)[2:-1]
        # Handle network name "\x00\x00\x00\x00\x00\x00\x00\x00\x00" (nine ASCII null characters)
        if ssid_raw_str.startswith('\\x'):
            # Replace ASCII null characters with the bytes equivalent of an empty string
            ssid_raw: bytes = ssid_raw.replace(b'\x00', ''.encode('ascii'))
            ssid: str = ssid_raw.decode('ascii')
        else:
            ssid: str = specs[0].decode('utf-8')

        bssid: str = binascii.hexlify(specs[1], '-').decode()
        channel: int = specs[2]
        rssi: int = specs[3]

        # TODO check hidden values are valid
        # hidden should have 2 options but in specs tuple it's 1, 2, 3 or 5.

        security: int = specs[4]
        hidden: int = specs[5]

        network = cls(wlan, ssid, bssid, channel, rssi, security, hidden)
        return network

    @property
    def bssid(self) -> str:
        return self._bssid

    @property
    def channel(self) -> int:
        return self._channel

    def connect(self) -> None:
        if not self._password:
            raise AttributeError(
                f'Password is not specified for WiFiNetwork "{self.ssid}"')

        wlan = self._wlan
        wlan.connect(self.ssid, self._password)

        max_wait = 10
        while max_wait > 0:
            if self.status.Failed or self.status.Success:
                break
            max_wait -= 1
            # print('\t- Waiting for connection...')
            time.sleep(1)

        if self._wlan.status() != WiFiStatus.GotIP:
            raise RuntimeError('network connection failed')
        else:
            print(
                f'Connected to "{self.ssid}" (IP address: {self._wlan.ifconfig()[0]})\n')

    @property
    def hidden(self) -> int:
        return self._hidden

    @property
    def name(self) -> str:
        return self.ssid

    @property
    def password(self) -> AttributeError:
        raise AttributeError(
            'Getting of a WiFiNetwork\'s password is not supported')

    @password.setter
    def password(self, password: str) -> None:
        self._password = password

    @property
    def rssi(self) -> int:
        return self._rssi

    @property
    def security(self) -> int:
        return self._security

    @property
    def ssid(self) -> str:
        return self._ssid

    @property
    def status(self) -> WiFiStatus:
        return WiFiStatus._match(self._wlan.status())


def connect_to_wifi() -> None:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    with open('.networks.json', 'r') as f:
        known_networks_json: dict[str, dict[str, str]] = json.load(f)

    # Get network names from .networks.json's keys
    known_network_names: list[str] = list(known_networks_json.keys())

    # WiFi: (ssid, bssid, channel, RSSI, security, hidden)
    networks_raw: list[tuple[bytes, bytes, int, int, int, int]] = wlan.scan()
    # networks_raw: list[tuple[bytes, bytes, int, int, int, int]] = [(b'VM1274792', b'd\x18\xdf%\xd8=', 1, -81, 5, 2), (b'TP-Link_AC5E', b'\xd8\r\x17\x17\xac^', 3, -93, 5, 1), (b'Y\xcf\x86', b'\x00#j\xfc\xf64', 1, -67, 5, 1), (b'VM7461507', b'$K\xfe\xe6\x1d\x81', 3, -77, 5, 5),
    #                                                                (b'DIRECT-9E-HP ENVY 5000 series', b'J\xbaN\xc8M\x9e', 1, -82, 5, 3), (b'EE-27JWSC', b'\xa0-\xdb\xf5\xb5\x82', 11, -77, 5, 2), (
    #                                                                    b'EE WiFi', b'\n-\xdb\xf5\xb5\x83', 11, -78, 0, 2), (b'BT-TTAFGC', b'\x0c\x8e)3\xdcV', 11, -93, 5, 1),
    #                                                                # Mocking network with SSID "\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    #                                                                (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00',
    #                                                                 b'', 11, -30, 5, 6)]

    available_networks = [WiFiNetwork.from_tuple(
        wlan, net) for net in networks_raw]

    known_available_networks: list[WiFiNetwork] = [
        network for network in available_networks if network.name in known_network_names]

    # Set passwords for known networks
    for net in known_available_networks:
        password: str = known_networks_json[net.name]['password']
        net.password = password

    num_known_available_networks = len(known_available_networks)
    wifi_to_connect: WiFiNetwork
    if num_known_available_networks == 0:
        raise CouldNotConnectError('No known networks are available')
    elif num_known_available_networks == 1:
        wifi_to_connect = known_available_networks[0]
    # num_known_available_networks > 1. Connect to the network with the strongest signal (highest RSSI).
    else:
        # Sort known_available_networks by ascending RSSI
        known_available_networks.sort(key=lambda net: net.rssi)
        strongest_network = known_available_networks[-1]
        wifi_to_connect = strongest_network

    wifi_to_connect.connect()
