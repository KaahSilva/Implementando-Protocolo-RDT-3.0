import socket
import zlib
import threading
import random

class RDT3_0:
    def __init__(self, sock, timeout=2, loss_prob=0.1, corrupt_prob=0.1):
        self.sock = sock
        self.timeout = timeout
        self.seq_num = 0  # Número de sequência inicial.
        self.expected_seq_num = 0  # Número de sequência esperado.
        self.timer = None
        self.loss_prob = loss_prob  # Probabilidade de perda de pacote.
        self.corrupt_prob = corrupt_prob  # Probabilidade de corrupção de pacote.

    def calculate_checksum(self, data):
        return zlib.crc32(data.encode('utf-8'))

    def make_pkt(self, seq_num, data):
        checksum = self.calculate_checksum(data)
        return f"{seq_num}|{checksum}|{data}".encode('utf-8')

    def udt_send(self, pkt, addr):
        # Simula a perda e corrupção de pacotes
        if random.random() < self.loss_prob:
            print("Simulando perda de pacote...")
            return  # Simula a perda do pacote (não envia)
        
        if random.random() < self.corrupt_prob:
            print("Simulando corrupção de pacote...")
            pkt = self.corrupt_packet(pkt)  # Simula a corrupção do pacote

        self.sock.sendto(pkt, addr)

    def corrupt_packet(self, pkt):
        # Introduz uma corrupção no pacote
        return pkt[:-1] + b'x'

    def receive(self):
        self.sock.settimeout(self.timeout)
        try:
            data, addr = self.sock.recvfrom(1024)
            data_str = data.decode('utf-8')
            seq_num_str, checksum_str, payload = data_str.split('|', 2)
            seq_num = int(seq_num_str)
            checksum = int(checksum_str)

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

    def rdt_send(self, data, addr):
        # Estado (a) e (f) - Envio do pacote
        sndpkt = self.make_pkt(self.seq_num, data)  # (a) e (f)
        self.udt_send(sndpkt, addr)  # (a) e (f)
        self.start_timer(addr, sndpkt)  # (a) e (f)

        # Estado (b) e (g) - Espera por ACK ou timeout
        while True:
            if self.wait_for_ack():
                # Estado (d) e (i) - Recebeu ACK corretamente
                self.stop_timer()  # (d) e (i)
                self.seq_num = 1 - self.seq_num  # Alterna entre 0 e 1.
                break
            else:
                # Estado (c) e (g) - Timeout ou erro, retransmite o pacote
                print("Timeout ou erro no ACK, retransmitindo o pacote...")  # (c) e (g)
                self.udt_send(sndpkt, addr)  # (c) e (g)
                self.start_timer(addr, sndpkt)  # (c) e (g)

    def rdt_rcv(self):
        # Estado (e) e (j) - Recepção de dados
        while True:
            seq_num, payload, addr = self.receive()
            if seq_num is not None:
                if seq_num == self.expected_seq_num:
                    print(f"Recebido: {payload}")
                    self.send_ack(seq_num, addr)
                    self.expected_seq_num = 1 - self.expected_seq_num  # Alterna entre 0 e 1.
                    return payload  # Retorna o dado recebido.
                else:
                    # Estado (g) - Pacote duplicado ou corrompido, reenviando ACK.
                    print("Pacote duplicado, reenviando ACK.")
                    self.send_ack(1 - self.expected_seq_num, addr)

    def start_timer(self, addr, sndpkt):
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.udt_send, [sndpkt, addr])
        self.timer.start()
        print("Timer iniciado.")  # (a) e (f)

    def stop_timer(self):
        if self.timer is not None:
            self.timer.cancel()
        print("Timer parado.")  # (d) e (i)