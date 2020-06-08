import socket
import sys
import os

CHUNK_SIZE = 1024
DELIMITER = ':'
MAX_TIMEOUTS = 10

def download_file(server_address, name, dst):
  index = dst.rfind('/')
  folder = dst[:index]
  if not os.path.exists(folder):
    print("Creating dst")
    os.makedirs(folder, exist_ok=True)


  print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))
  cli_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  cli_socket.settimeout(1)

  request_acked, response = send_upload_request('download:{}'.format(name), cli_socket, server_address)
  if not request_acked:
    print('Could not send request to server. Program exiting')
    return exit(1)

  if response == 'File not found':
    print(response)
    return exit(1)

  total_packets = int(response)
  send_upload_request('ok', cli_socket, server_address)
  recv_file(cli_socket, server_address, dst, int(total_packets))
  cli_socket.close()


def send_upload_request(request, cli_socket, server_address):
  #Example request: "download:filename.txt"
  for i in range(MAX_TIMEOUTS):
    cli_socket.sendto(request.encode(), server_address)
    try:
      response, addr = cli_socket.recvfrom(CHUNK_SIZE)
      return True, response.decode()
    except socket.timeout:
      print('Timeout number {} - Request: {}'.format(str(i), request))
  return False, ''


def recv_file(cli_socket, server_address, filename, total_packets):
  packets = {}
  recvd_packets = 0
  timeouts = 0

  while (recvd_packets < total_packets) and (timeouts < MAX_TIMEOUTS):
    try:
      packet, addr = cli_socket.recvfrom(CHUNK_SIZE)
      packet_seq_no, chunk = packet.decode().split(DELIMITER, 1)
      if packet_seq_no == "upload":
        return 1

      timeouts = 0
      cli_socket.sendto(packet_seq_no.encode(), server_address)
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

  write_file(packets, filename)


def write_file(packets, filename):
  file = open(filename, "wb")
  for i in range(0, len(packets)):
    file.write(packets[str(i)].encode())
  file.close()
  print('Success downloading file')