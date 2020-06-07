import socket
import os

CHUNK_SIZE = 1024

def upload_file(server_address, src, name):
  # TODO: Implementar TCP upload_file client
  print('TCP: upload_file({}, {}, {})'.format(server_address, src, name))

  f = open(src, "rb")
  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)

  print("Sending {} bytes from {}".format(size, src))

  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(server_address)

  sock.send(b'upload')
  confirmation = sock.recv(CHUNK_SIZE)
  assert confirmation == b'ok'

  sock.send(name.encode())

  sock.send(str(size).encode())
  signal = sock.recv(CHUNK_SIZE)

  if signal.decode() != "start":
    print("There was an error on the server")
    return exit(1)

  while True:
    chunk = f.read(CHUNK_SIZE)
    if not chunk:
      break
    sock.send(chunk)

  print("Sent files")

  f.close()
  sock.close()