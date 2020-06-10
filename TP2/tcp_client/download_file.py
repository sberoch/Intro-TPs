import socket, os

DELIMITER = ':'
CHUNK_SIZE = 1024

def download_file(server_address, name, dst):

  print(f'TCP: download_file({server_address}, {name}, {dst})')
  index = dst.rfind('/')
  folder = dst[:index]
  if not os.path.exists(folder):
    print("Creating dst folder")
    os.makedirs(folder, exist_ok=True)

  # Create socket and connect to server
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
  except ConnectionError:
    print("Unable to contact remote server, aborting")
    return exit(1)

  message = 'download' + DELIMITER + name

  sock.send(message.encode())

  filesize = sock.recv(CHUNK_SIZE).decode()

  if int(filesize) < 0:
    print(f"File not found on server, exiting")
    sock.close()
    return exit(1)

  print(f"TCP: Receiving {filesize} bytes")

  try:
    f = open(dst, "wb")
  except OSError:
    print(f"Error while creating local-file {dst}, exiting...")
    sock.send(b'error')
    sock.close()
    return exit(1)

  bytes_recvd = 0

  sock.send(b'start')

  while bytes_recvd < int(filesize):
    data = sock.recv(CHUNK_SIZE)
    bytes_recvd += len(data)
    f.write(data)

  print(f"Downloaded file {dst}, total bytes {bytes_recvd}")
  assert bytes_recvd == int(filesize)


  f.close()
  sock.close()
