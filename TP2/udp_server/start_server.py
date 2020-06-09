import socket
import os

CHUNK_SIZE = 1024
DELIMITER = ':'
MAX_TIMEOUTS = 10
MAX_PACKETS_PER_WINDOW = 10

def start_server(server_address, storage_dir):
  if not os.path.exists(storage_dir):
    print("Creando storage_dir")
    os.makedirs(storage_dir, exist_ok=True)

  print('UDP: start_server({}, {})'.format(server_address, storage_dir))
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(server_address)

  try:
    run_server(sock, storage_dir)

  except Exception as e:
    print(e)
    return exit(1)

  finally:
    sock.close()


def run_server(svr_socket, storage_dir):
  while True:
    svr_socket.settimeout(None)
    request, addr = svr_socket.recvfrom(CHUNK_SIZE)
    request = request.decode()
    try:
      command, info = request.split(DELIMITER, 1)
    except ValueError:
      continue

    if command == 'upload':
      filename, total_packets = info.split(DELIMITER, 1)
      print('Requested: upload file {} with {} packets'.format(filename, total_packets))
      svr_socket.sendto(b'ok', addr)

      recv_file(svr_socket, addr, storage_dir+'/'+filename, int(total_packets))

    elif command == 'download':
      svr_socket.settimeout(0.1)
      filename = storage_dir+'/'+info
      if os.path.exists(filename):
        send_file_info(filename, svr_socket, addr)
      else:
        svr_socket.sendto(b'File not found', addr)
    else:
      continue

#TODO: error raro cada tanto no puede mandar archivo
def recv_file(svr_socket, addr, filename, total_packets):
  packets = {}
  recvd_packets = 0
  timeouts = 0
  svr_socket.settimeout(0.1)

  while (recvd_packets < total_packets) and (timeouts < MAX_TIMEOUTS):
    try:
      packet, addr = svr_socket.recvfrom(CHUNK_SIZE)
      packet_seq_no, chunk = packet.decode().split(DELIMITER, 1)
      if packet_seq_no == "upload":
        return 1

      timeouts = 0
      svr_socket.sendto(packet_seq_no.encode(), addr)
      if packet_seq_no not in packets:
        packets[packet_seq_no] = chunk
        recvd_packets += 1

    except socket.timeout:
      print('Timeout {}'.format(str(timeouts)))
      timeouts += 1
      continue

  if timeouts >= MAX_TIMEOUTS:
      print('Could not receive file.')
      return 1

  svr_socket.sendto(b'done', addr)
  write_file(packets, filename)


def write_file(packets, filename):
  file = open(filename, "wb")
  for i in range(0, len(packets)):
    file.write(packets[str(i)].encode())
  file.close()
  print('Success uploading file')


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

def send_file_info(filename, svr_socket, cli_addr):
  packets = load_file(filename)
  for i in range(MAX_TIMEOUTS):
    svr_socket.sendto(str(len(packets)).encode(), cli_addr)
    try:
      ack, addr = svr_socket.recvfrom(CHUNK_SIZE)
      send_file(packets, svr_socket, cli_addr)
      break
    except socket.timeout:
      print('Timeout sending file info.')
  return 1


def send_file(packets, svr_socket, cli_addr):
  sent_packets = 0
  total_packets = len(packets)
  timeouts = 0

  while (sent_packets < total_packets) and (timeouts < MAX_TIMEOUTS):
    packets_seq_numbers = list(packets.keys())
    remaining_packets = total_packets - sent_packets
    packets_to_send = remaining_packets if remaining_packets < MAX_PACKETS_PER_WINDOW else MAX_PACKETS_PER_WINDOW

    for i in range(packets_to_send):
      svr_socket.sendto(packets[packets_seq_numbers[i]].encode(), cli_addr)

    for j in range(packets_to_send):
      try:
        response, addr = svr_socket.recvfrom(CHUNK_SIZE)
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
    print('Could not send file to client.')
