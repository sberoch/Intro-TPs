import socket

CHUNK_SIZE = 1024

def download_file(server_address, name, dst):
  # TODO: Implementar UDP download_file client
  print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  sock.sendto(b'download', server_address)
  sock.sendto(name.encode(), server_address)
  filesize, addr = sock.recvfrom(CHUNK_SIZE)

  print('UDP: receiving {} bytes'.format(filesize.decode()))
  sock.close()