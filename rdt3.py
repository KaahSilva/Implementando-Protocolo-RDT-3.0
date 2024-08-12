import socket
import zlib

class RDT3_0:
    def __init__(self, sock, timeout=1):
        self.sock = sock
        self.timeout = timeout
        self.seq_num = 0  # Número de sequência inicial.
        self.expected_seq_num = 0  # Número de sequência esperado para o próximo pacote.

    def calculate_checksum(self, data):
        # Calcula o checksum (usado em várias partes).
        return zlib.crc32(data.encode('utf-8'))

    def make_pkt(self, seq_num, data):
        # Cria um pacote com número de sequência, checksum e dados.
        checksum = self.calculate_checksum(data)
        return f"{seq_num}|{checksum}|{data}".encode('utf-8')

    def udt_send(self, pkt, addr):
        # Envia o pacote pela rede não confiável.
        self.sock.sendto(pkt, addr)

    def receive(self):
        # Recebe um pacote e verifica a integridade.
        self.sock.settimeout(self.timeout)
        try:
            data, addr = self.sock.recvfrom(1024)
            data_str = data.decode('utf-8')
            seq_num_str, checksum_str, payload = data_str.split('|', 2)
            seq_num = int(seq_num_str)
            checksum = int(checksum_str)

            # Verifica o checksum para detectar corrupção do pacote.
            if checksum == self.calculate_checksum(payload):
                return seq_num, payload, addr
            else:
                print("Checksum inválido. Pacote corrompido.")
                return None, None, None
        except socket.timeout:
            return None, None, None

    def send_ack(self, seq_num, addr):
        # Envia um pacote de ACK para o remetente.
        ack_pkt = self.make_pkt(seq_num, "ACK")
        self.udt_send(ack_pkt, addr)

    def wait_for_ack(self):
        # Espera o recebimento de um ACK.
        seq_num, payload, addr = self.receive()
        if seq_num == self.seq_num and payload == "ACK":
            return True
        return False

    def rdt_send(self, data, addr):
        # Estado (a) e (f) - Mesmo código para os estados "Wait for call 0/1 from above"
        sndpkt = self.make_pkt(self.seq_num, data)  # (a) e (f)
        self.udt_send(sndpkt, addr)  # (a) e (f)
        self.start_timer()  # (a) e (f)

        # Transição para o estado (b) ou (g)
        while True:
            if self.wait_for_ack():
                # Estado (d) e (i) - Recebeu ACK corretamente, para o timer
                self.stop_timer()  # (d) e (i)
                self.seq_num = 1 - self.seq_num  # Alterna entre 0 e 1.
                break
            else:
                # Estado (c) e (g) - Timeout ou erro, retransmite o pacote
                print("Timeout ou erro no ACK, retransmitindo o pacote...")  # (c) e (g)
                self.udt_send(sndpkt, addr)  # (c) e (g)
                self.start_timer()  # (c) e (g)

    def rdt_rcv(self):
        # Estado (e) e (j) - Mesmo código para esperar a chamada de cima.
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

    def start_timer(self):
        # Simula o início do temporizador.
        print("Timer iniciado.")

    def stop_timer(self):
        # Simula a parada do temporizador.
        print("Timer parado.")
