import socket
import os

CHUNK_SIZE = 1024
DELIMITER = ':'

def upload_file(server_address, src, name):
  print('TCP: upload_file({}, {}, {})'.format(server_address, src, name))

  try:
    f = open(src, "rb")
  except FileNotFoundError:
    print(f"File {src} not found.")
    return exit(1)

  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)

  print("Sending {} bytes from {}".format(size, src))

  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(server_address)

  message = 'upload' + DELIMITER + name + DELIMITER + str(size)
  sock.send(message.encode())
  signal = sock.recv(CHUNK_SIZE)

  if signal.decode() != "start":
    print("There was an error on the server")
    f.close()
    return exit(1)

  while True:
    chunk = f.read(CHUNK_SIZE)
    if not chunk:
      break
    sock.send(chunk)

  print("File sent correctly!")

  f.close()
  sock.close()