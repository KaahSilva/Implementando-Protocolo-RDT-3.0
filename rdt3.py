import socket
import threading
import time

import struct

TIMEOUT = 1.0  # Timeout de 1 segundo
ACK = b'ACK'

class RDT_Socket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.lock = threading.Lock()
        self.expected_seqnum = 0
        self.next_seqnum = 0
        self.ack_received = threading.Event()
        self.state = 'WAIT_CALL_0_FROM_ABOVE'

    def make_pkt(self, seqnum, data):
        checksum = sum(data) % 256  # Simples checksum
        return struct.pack('!I', seqnum) + struct.pack('!B', checksum) + data

    def is_corrupt(self, packet):
        received_checksum = packet[4]
        data = packet[5:]
        calculated_checksum = sum(data) % 256
        return received_checksum != calculated_checksum

    def is_ack(self, packet, seqnum):
        ack_seqnum = struct.unpack('!I', packet[:4])[0]
        return ack_seqnum == seqnum

    def rdt_send(self, data, addr):
        while True:
            if self.state == 'WAIT_CALL_0_FROM_ABOVE':
                # a) rdt_send(data)
                sndpkt = self.make_pkt(0, data)
                self.sock.sendto(sndpkt, addr)
                self.start_timer()
                self.state = 'WAIT_ACK_0'

            elif self.state == 'WAIT_ACK_0':
                try:
                    rcvpkt, _ = self.sock.recvfrom(1024)
                    # b) rdt_rcv(rcvpkt) && (corrupt(rcvpkt) || isACK(rcvpkt,1))
                    if self.is_corrupt(rcvpkt) or self.is_ack(rcvpkt, 1):
                        continue
                    # d) rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && isACK(rcvpkt,0)
                    if not self.is_corrupt(rcvpkt) and self.is_ack(rcvpkt, 0):
                        self.stop_timer()
                        self.state = 'WAIT_CALL_1_FROM_ABOVE'
                        break
                except socket.timeout:
                    # c) timeout
                    self.sock.sendto(sndpkt, addr)
                    self.start_timer()

            elif self.state == 'WAIT_CALL_1_FROM_ABOVE':
                # f) rdt_send(data)
                sndpkt = self.make_pkt(1, data)
                self.sock.sendto(sndpkt, addr)
                self.start_timer()
                self.state = 'WAIT_ACK_1'

            elif self.state == 'WAIT_ACK_1':
                try:
                    rcvpkt, _ = self.sock.recvfrom(1024)
                    # g) rdt_rcv(rcvpkt) && (corrupt(rcvpkt) || isACK(rcvpkt,0))
                    if self.is_corrupt(rcvpkt) or self.is_ack(rcvpkt, 0):
                        continue
                    # i) rdt_rcv(rcvpkt) && notcorrupt(rcvpkt) && isACK(rcvpkt,1)
                    if not self.is_corrupt(rcvpkt) and self.is_ack(rcvpkt, 1):
                        self.stop_timer()
                        self.state = 'WAIT_CALL_0_FROM_ABOVE'
                        break
                except socket.timeout:
                    # g) timeout
                    self.sock.sendto(sndpkt, addr)
                    self.start_timer()

    def rdt_recv(self, bufsize):
        while True:
            try:
                packet, addr = self.sock.recvfrom(bufsize)
                # e) rdt_rcv(rcvpkt)
                if self.is_corrupt(packet):
                    continue
                seqnum = struct.unpack('!I', packet[:4])[0]
                if seqnum == self.expected_seqnum:
                    self.expected_seqnum = 1 - self.expected_seqnum
                    ack_pkt = self.make_pkt(seqnum, ACK)
                    self.sock.sendto(ack_pkt, addr)
                    return packet[5:], addr
            except socket.timeout:
                continue

    def start_timer(self):
        self.timer = threading.Timer(TIMEOUT, self.handle_timeout)
        self.timer.start()

    def stop_timer(self):
        self.timer.cancel()

    def handle_timeout(self):
        self.ack_received.clear()

def rdt_socket():
    return RDT_Socket()

def rdt_bind(sock, port):
    sock.sock.bind(('', port))

def rdt_peer(sock, address, port):
    sock.sock.connect((address, port))

def rdt_send(sock, data, addr=None):
    sock.rdt_send(data, addr)

def rdt_recv(sock, bufsize):
    return sock.rdt_recv(bufsize)

def rdt_close(sock):
    sock.sock.close()

def rdt_network_init(loss_prob, corrupt_prob):
    pass  # Implementação fictícia para simular a inicialização da rede
