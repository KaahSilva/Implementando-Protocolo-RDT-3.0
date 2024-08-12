import socket
from rdt import RDT3_0

# Configuração do socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 8080)
rdt = RDT3_0(sock=client_socket)

try:
    # Solicita um número ao usuário
    message = input("Digite um número: ")

    # Envia o número para o servidor
    request_pkt = rdt.make_pkt(rdt.seq_num, message)
    rdt.udt_send(request_pkt, server_address)
    
    # Espera pela resposta do servidor
    while True:
        seq_num, data, server = rdt.receive()
        if data is None:
            continue

        print(f"Resposta do servidor: {data}")

        # Envia o ACK para o servidor
        rdt.send_ack(seq_num, server)

        # Confere se o pacote é o esperado
        if seq_num == rdt.expected_seq_num:
            rdt.expected_seq_num = 1 - rdt.expected_seq_num  # Alterna o número de sequência esperado
            break

except Exception as e:
    print(f"Erro: {e}")
    
finally:
    # Fecha o socket do cliente
    client_socket.close()
