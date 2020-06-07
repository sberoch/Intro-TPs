import socket, os

CHUNK_SIZE = 1024

def download_file(server_address, name, dst):
  # TODO: Implementar TCP download_file client

  print(f'TCP: download_file({server_address}, {name}, {dst})')

  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect(server_address)

  sock.send(b'download')

  confirmation = sock.recv(CHUNK_SIZE)

  sock.send(name.encode())

  filesize = sock.recv(CHUNK_SIZE).decode()

  print(f"TCP: Receiving {filesize} bytes")

  sock.send(b'start')

  f = open(dst, "wb")
  bytes_recvd = 0

  while bytes_recvd < int(filesize):
    data = sock.recv(CHUNK_SIZE)
    bytes_recvd += len(data)
    f.write(data)

  print(f"Downloaded file {dst}, total bytes {bytes_recvd}")
  assert bytes_recvd == int(filesize)



  sock.close()
