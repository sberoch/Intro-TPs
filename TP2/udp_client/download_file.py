import socket
import sys

CHUNK_SIZE = 1024

def download_file(server_address, name, dst):
  # TODO: Implementar UDP download_file client
  print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  sock.sendto(b'download', server_address)
  signal, addr = sock.recvfrom(CHUNK_SIZE)

  sock.sendto(name.encode(), server_address)
  filesize, addr = sock.recvfrom(CHUNK_SIZE)

  if (filesize < 0):
  	print("File not found on the server")
    return exit(1)

  print('UDP: receiving {} bytes'.format(filesize.decode()))
  sock.sendto(b'start', server_address)

  file = open(dst, "wb")
  received = 0
  while received < int(filesize.decode()):
  	data, addr = sock.recvfrom(CHUNK_SIZE)
  	received += len(data)
  	file.write(data)

  print('UDP: received {} bytes'.format(received))
  # Send number of bytes received
  sock.sendto(str(received).encode(), server_address)

  file.close()
  sock.close()