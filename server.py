import socket
from rdt import RDT3_0

# Configuração do socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 8080)
server_socket.bind(server_address)
print("Servidor UDP iniciado com RDT3.0 e Checksum. Aguardando conexões...")

rdt = RDT3_0(sock=server_socket)

while True:
    try:
        # Recebe o pacote do cliente
        seq_num, data, client_address = rdt.receive()

        if data is None:
            continue

        print(f"Dados recebidos de {client_address}: {data}")

        try:
            # Converte a string recebida para um número inteiro
            num = int(data)
            if num % 2 == 0:
                response = "PAR"
            else:
                response = "ÍMPAR"
        except ValueError:
            response = "ENTRADA INVÁLIDA"

        # Envia a resposta para o cliente
        response_pkt = rdt.make_pkt(rdt.seq_num, response)
        rdt.udt_send(response_pkt, client_address)
        print(f"Resposta enviada para {client_address}: {response}")

        # Espera pelo ACK
        if rdt.wait_for_ack():
            print("ACK recebido. Mensagem entregue com sucesso.")
            rdt.seq_num = 1 - rdt.seq_num  # Alterna o número de sequência após o ACK
        else:
            print("ACK não recebido ou corrompido. Reenviando a resposta.")
            rdt.udt_send(response_pkt, client_address)

    except Exception as e:
        print(f"Erro: {e}")
        break

server_socket.close()
