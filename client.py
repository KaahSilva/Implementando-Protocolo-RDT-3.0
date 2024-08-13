import socket
from rdt3 import RDT3_0

# Configuração do socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('10.24.31.143', 5000)  # Substitua pelo IP da máquina do servidor
rdt = RDT3_0(sock=client_socket)

try:
    message = input("Digite um número: ")
    request_pkt = rdt.make_pkt(rdt.seq_num, message)
    rdt.udt_send(request_pkt, server_address)
    
    while True:
        seq_num, data, server = rdt.receive()
        if data is None:
            continue

        print(f"Resposta do servidor: {data}")
        rdt.send_ack(seq_num, server)

        if seq_num == rdt.expected_seq_num:
            rdt.expected_seq_num = 1 - rdt.expected_seq_num
            break

except Exception as e:
    print(f"Erro: {e}")
    
finally:
    client_socket.close()
