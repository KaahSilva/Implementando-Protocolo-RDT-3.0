import socket
import time

class RDT3_0:
    def __init__(self, sock=None, server_port=None, client_port=None):
        self.server_port = server_port
        self.client_port = client_port
        self.seq_num = 0
        self.timeout = 1
        self.max_seq_num = 1000000
        self.sock = sock  # Recebe o socket criado externamente

    # Função para enviar dados
    def send(self, data, addr):
        sndpkt = self.make_pkt(self.seq_num, data.decode())
        self.udt_send(sndpkt, addr)

        start_timer = self.start_timer()

        while True:
            if self.check_timeout(start_timer):
                print("Timeout, reenviando...")
                self.udt_send(sndpkt, addr)
                start_timer = self.start_timer()
                continue

            try:
                rcvpkt = self.udt_recv()
                if self.isACK(rcvpkt, self.seq_num):
                    self.stop_timer(start_timer)
                    break
            except Exception as e:
                print(f"Erro durante o recebimento do ACK: {e}")

    # Função para receber dados
    def receive(self, addr):
        rcvpkt = self.udt_recv()
        print(f"Dados recebidos: {rcvpkt.decode()}")
        
        try:
            seq_num, data = rcvpkt.decode().split("|", 1)
            seq_num = int(seq_num)
            
            # Envia ACK para o pacote recebido
            self.udt_send(self.make_ack(seq_num), addr)
        except Exception as e:
            print(f"Erro durante o processamento dos dados recebidos: {e}")

    # Função para criar um pacote
    def make_pkt(self, seq_num, data):
        return (str(seq_num) + "|" + data).encode()

    # Função para criar um ACK
    def make_ack(self, seq_num):
        return (str(seq_num) + "|ACK").encode()

    # Função para enviar dados pela UDP
    def udt_send(self, sndpkt, addr):
        self.sock.sendto(sndpkt, addr)

    # Função para receber dados pela UDP
    def udt_recv(self):
        data, addr = self.sock.recvfrom(1024)
        return data

    # Função para iniciar o temporizador
    def start_timer(self):
        return time.time()

    # Função para parar o temporizador
    def stop_timer(self, start_timer):
        pass  # Se não precisar fazer nada, pode deixar assim

    # Função para verificar o tempo limite
    def check_timeout(self, start_timer):
        return (time.time() - start_timer) > self.timeout

    # Função para verificar se o ACK é válido
    def isACK(self, rcvpkt, seq_num):
        decoded_pkt = rcvpkt.decode()
        parts = decoded_pkt.split("|")
        return len(parts) == 2 and parts[0] == str(seq_num) and parts[1] == "ACK"