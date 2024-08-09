from rdt3 import rdt_socket, rdt_peer, rdt_send, rdt_recv, rdt_close, rdt_network_init

def cliente():
    rdt_network_init(0.0, 0.0)  # Inicializa a rede com taxas de perda e erro de 0
    sock = rdt_socket()
    rdt_peer(sock, "localhost", 200)  # IP e porta do servidor

    while True:
        try:
            numero = input("Digite um número (ou 'exit' para sair): ")
            if numero.lower() == 'exit':
                break
            rdt_send(sock, numero.encode())
            resposta, _ = rdt_recv(sock, 1024)
            print("Resposta do servidor:", resposta.decode())
        except Exception as e:
            print("Erro no cliente:", e)
            break
    
    rdt_close(sock)

if __name__ == "__main__":
    cliente()
#----------------------------------
import socket

# Defina o endereço IP e a porta do servidor
SERVER_ADDRESS = ("127.0.0.1", 12000)  # Certifique-se de que esta linha esteja correta

# Crie um socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    message = input("Digite um número (ou 'exit' para sair): ")
    if message.lower() == 'exit':
        break
    try:
        # Envie a mensagem ao servidor
        client_socket.sendto(message.encode(), SERVER_ADDRESS)
        
        # Receba a resposta do servidor
        response, server = client_socket.recvfrom(2048)
        print("Resposta do servidor:", response.decode())
    except Exception as e:
        print(f"Erro no cliente: {e}")

# Feche o socket
client_socket.close()
