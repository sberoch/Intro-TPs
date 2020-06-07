import socket
import os
import hashlib

CHUNK_SIZE = 1024

def upload_file(server_address, src, name):
  # TODO: Implementar UDP upload_file client

  if not os.path.exists(src):
    print("File not found")
    return exit(1)

  print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))

  f = open(src, "rb")
  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)

  print("Sending {} bytes from {}".format(size, src))

  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.settimeout(0.2)

  sock.sendto(b'upload', server_address)
  signal, addr = sock.recvfrom(CHUNK_SIZE)

  sock.sendto(str(size).encode(), server_address)
  signal, addr = sock.recvfrom(CHUNK_SIZE)

  sock.sendto(name.encode(), server_address)
  signal, addr = sock.recvfrom(CHUNK_SIZE)

  if signal.decode() != "start":
    print("There was an error on the server")
    return exit(1)

  upload_data(sock, f, server_address)

  # Recv amount of data received by the server
  num_bytes, addr = sock.recvfrom(CHUNK_SIZE)
  print("Received {} bytes".format(num_bytes.decode()))

  f.close()
  sock.close()

def upload_data(sock, f, server_address):

  #checksum:data

  packet = ''
  seq_no = 0
  while True:
    datachunk = f.read(CHUNK_SIZE)
    if not datachunk:
      break

    packet = ''
    packet += hashlib.md5(datachunk).hexdigest() + ':'
    packet += str(datachunk)
    
    while True:
      sock.sendto(packet, server_address)
      try:
        ack, addr = sock.recvfrom(CHUNK_SIZE)
        break
      except:
        continue