
import socket
import threading
from rdt3 import RDT3_0

class Server:
    def __init__(self, server_port):
        self.server_port = server_port

        # Cria um socket UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.server_port))

        # Cria uma instância de RDT3.0, passando o socket
        self.rdt = RDT3_0(sock=self.sock)

    def start(self):
        while True:
            try:
                # Recebe o dado do cliente
                rcvpkt, addr = self.sock.recvfrom(1024)  # Recebe o pacote e o endereço
                print(f"Dados recebidos do cliente: {rcvpkt.decode()}")
                
                # Processa o pacote recebido do cliente
                self.rdt.receive(addr)  # Processa o ACK primeiro
                
                # Extraí o número e os dados
                seq_num, received_data = rcvpkt.decode().split("|", 1)
                seq_num = int(seq_num)
                
                # Processa o número
                number = int(received_data)
                if number > 0:
                    response = "O número é positivo"
                else:
                    response = "O número é negativo"
                
                print(f"Enviando resposta: {response}")
                self.rdt.send(response.encode(), addr)
            except Exception as e:
                print(f"Erro ocorreu: {e}")

        self.sock.close()

# Executa o servidor
if __name__ == "__main__":
    server_port = 12345
    server = Server(server_port)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()
