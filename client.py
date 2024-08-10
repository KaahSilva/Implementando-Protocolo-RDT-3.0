import socket
from rdt3 import RDT3_0

class Client:
    def __init__(self, server_port, client_port):
        self.server_port = server_port
        self.client_port = client_port

        # Cria um socket UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.client_port))

        # Cria uma instância de RDT3.0, passando o socket
        self.rdt = RDT3_0(sock=self.sock)

    def start(self, server_addr):
        while True:
            try:
                number = int(input("Digite um número: "))
                print(f"Enviando número: {number}")
                self.rdt.send(str(number).encode(), server_addr)
                data, _ = self.sock.recvfrom(1024)
                print(f"Recebido do servidor: {data.decode()}")
            except Exception as e:
                print(f"Erro ocorreu: {e}")

        self.sock.close()

# Executa o cliente
if __name__ == "__main__":
    server_port = 12345
    client_port = 54321
    server_addr = ("localhost", server_port)

    client = Client(server_port, client_port)
    client.start(server_addr)
