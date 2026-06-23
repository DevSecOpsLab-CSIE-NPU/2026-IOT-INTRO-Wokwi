# Minimal umqtt.simple-compatible client for MicroPython.
import usocket as socket
import ustruct as struct


class MQTTException(Exception):
    pass


class MQTTClient:
    def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={}):
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.pid = 0
        self.user = user
        self.pswd = password
        self.keepalive = keepalive

    def _send_str(self, s):
        self.sock.write(struct.pack('!H', len(s)))
        self.sock.write(s)

    def _recv_len(self):
        n = 0
        sh = 0
        while True:
            b = self.sock.read(1)[0]
            n |= (b & 0x7F) << sh
            if not b & 0x80:
                return n
            sh += 7

    def connect(self, clean_session=True):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        if self.ssl:
            import ussl
            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)

        premsg = bytearray(b'\x10\x00\x00\x04MQTT\x04\x02\x00\x00')
        msg = bytearray()
        sz = 10 + 2 + len(self.client_id)
        msg.extend(struct.pack('!H', len(self.client_id)))
        msg.extend(self.client_id)
        if self.user is not None:
            sz += 2 + len(self.user)
            msg.extend(struct.pack('!H', len(self.user)))
            msg.extend(self.user)
            premsg[7] |= 0x80
            if self.pswd is not None:
                sz += 2 + len(self.pswd)
                msg.extend(struct.pack('!H', len(self.pswd)))
                msg.extend(self.pswd)
                premsg[7] |= 0x40
        if clean_session:
            premsg[7] |= 0x02
        premsg[8] = self.keepalive >> 8
        premsg[9] = self.keepalive & 0xFF

        i = 1
        while sz > 0x7F:
            premsg[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz
        self.sock.write(premsg, i + 2)
        self.sock.write(msg)

        resp = self.sock.read(4)
        if resp[0] != 0x20 or resp[1] != 0x02:
            raise MQTTException('bad CONNACK')
        if resp[3] != 0:
            raise MQTTException(resp[3])
        return resp[2] & 1

    def disconnect(self):
        if self.sock:
            self.sock.write(b'\xe0\x00')
            self.sock.close()
            self.sock = None

    def ping(self):
        self.sock.write(b'\xc0\x00')

    def publish(self, topic, msg, retain=False, qos=0):
        pkt = bytearray(b'\x30\x00')
        if qos:
            pkt[0] |= qos << 1
        if retain:
            pkt[0] |= 0x01
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        i = 1
        while sz > 0x7F:
            pkt[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        self.sock.write(pkt, i + 1)
        self._send_str(topic)
        if qos > 0:
            self.pid += 1
            pid = self.pid
            self.sock.write(struct.pack('!H', pid))
        self.sock.write(msg)
        if qos == 1:
            op = self.sock.read(4)
            if op[0] != 0x40 or op[1] != 0x02:
                raise MQTTException('no PUBACK')
