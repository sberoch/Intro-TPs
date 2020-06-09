import socket
import os

CHUNK_SIZE = 1024
DELIMITER = ':'
MAX_TIMEOUTS = 10
MAX_PACKETS_PER_WINDOW = 10

def upload_file(server_address, src, name):
  if not os.path.exists(src):
    print('File not found')
    return exit(1)

  print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))
  packets = load_file(src)

  cli_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  cli_socket.settimeout(0.1)

  request_acked = send_upload_request('upload:{}:{}'.format(name, str(len(packets))), cli_socket, server_address)
  if not request_acked:
    print('Could not send request to server. Program exiting')
    return exit(1)

  send_file(packets, cli_socket, server_address)
  cli_socket.close()


def load_file(src):
  f = open(src, "rb")
  packets = {}
  packet_seq_no = 0
  while True:
    header = str(packet_seq_no) + DELIMITER
    chunk = f.read(CHUNK_SIZE - len(header))
    if not chunk:
      break

    packets[str(packet_seq_no)] = header + chunk.decode()
    packet_seq_no += 1

  f.close()
  return packets


def send_upload_request(request, cli_socket, server_address):
  #Example request: "upload:filename.txt:17"
  for i in range(MAX_TIMEOUTS):
    cli_socket.sendto(request.encode(), server_address)
    try:
      ack = cli_socket.recvfrom(CHUNK_SIZE)
      return True
    except socket.timeout:
      print('Timeout number {} sending upload request'.format(str(i)))
  return False


def send_file(packets, cli_socket, server_address):
  sent_packets = 0
  total_packets = len(packets)
  timeouts = 0

  while (sent_packets < total_packets) and (timeouts < MAX_TIMEOUTS):
    packets_seq_numbers = list(packets.keys())
    remaining_packets = total_packets - sent_packets
    packets_to_send = remaining_packets if remaining_packets < MAX_PACKETS_PER_WINDOW else MAX_PACKETS_PER_WINDOW

    for i in range(packets_to_send):
      cli_socket.sendto(packets[packets_seq_numbers[i]].encode(), server_address)

    for j in range(packets_to_send):
      try:
        response, addr = cli_socket.recvfrom(CHUNK_SIZE)
        ack = response.decode()
        if ack == 'done':
          print('Success sending file to client')
          return 0
        timeouts = 0
        if ack in packets_seq_numbers:
          sent_packets += 1
          packets.pop(ack)

      except socket.timeout:
        timeouts += 1
        print('Timeout {} sending file'.format(str(timeouts)))
        continue

  if timeouts >= MAX_TIMEOUTS:
    print('Could not send request to server. Program exiting')
    return exit(1)









