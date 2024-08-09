from rdt3 import rdt_socket, rdt_bind, rdt_recv, rdt_send, rdt_close, rdt_network_init

def verifica_numero(num):
    if num > 0:
        return "O número é positivo."
    elif num < 0:
        return "O número é negativo."
    else:
        return "O número é zero."

def servidor():
    rdt_network_init(0.0, 0.0)  # Inicializa a rede com taxas de perda e erro de 0
    sock = rdt_socket()
    rdt_bind(sock, 200)  # Porta do servidor

    while True:
        try:
            data, addr = rdt_recv(sock, 1024)
            if not data:
                break
            numero = float(data.decode())
            resultado = verifica_numero(numero)
            rdt_send(sock, resultado.encode(), addr)
        except Exception as e:
            print("Erro no servidor:", e)
            break
    
    rdt_close(sock)

if __name__ == "__main__":
    servidor()


#-----------------------------------------
import socket

SERVER_ADDRESS = ("127.0.0.1", 12000)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)

print("Servidor pronto para receber mensagens...")

while True:
    message, client_address = server_socket.recvfrom(2048)
    print(f"Mensagem recebida de {client_address}: {message.decode()}")
    modified_message = message.decode().upper()
    server_socket.sendto(modified_message.encode(), client_address)
