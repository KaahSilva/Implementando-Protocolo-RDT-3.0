import socket
import zlib

class RDT3_0:
    def __init__(self, sock, timeout=1):
        self.sock = sock
        self.timeout = timeout
        self.seq_num = 0
        self.expected_seq_num = 0

    def calculate_checksum(self, data):
        return zlib.crc32(data.encode('utf-8'))

    def make_pkt(self, seq_num, data):
        checksum = self.calculate_checksum(data)
        return f"{seq_num}|{checksum}|{data}".encode('utf-8')

    def udt_send(self, pkt, addr):
        self.sock.sendto(pkt, addr)

    def receive(self):
        self.sock.settimeout(self.timeout)
        try:
            data, addr = self.sock.recvfrom(1024)
            data_str = data.decode('utf-8')
            seq_num_str, checksum_str, payload = data_str.split('|', 2)
            seq_num = int(seq_num_str)
            checksum = int(checksum_str)

            # Verifica o checksum
            if checksum == self.calculate_checksum(payload):
                return seq_num, payload, addr
            else:
                print("Checksum inválido. Pacote corrompido.")
                return None, None, None
        except socket.timeout:
            return None, None, None

    def send_ack(self, seq_num, addr):
        ack_pkt = self.make_pkt(seq_num, "ACK")
        self.udt_send(ack_pkt, addr)

    def wait_for_ack(self):
        seq_num, payload, addr = self.receive()
        if seq_num == self.seq_num and payload == "ACK":
            return True
        return False