import socket, os

CHUNK_SIZE = 1024

def start_server(server_address, storage_dir):
  # TODO: Implementar TCP server
  print('TCP: start_server({}, {})'.format(server_address, storage_dir))

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind(server_address)
  sock.listen(50)

  while True:
    conn, addr = sock.accept()
    if not conn:
      break

    print("Accepted connection from {}".format(addr))
    action = conn.recv(CHUNK_SIZE).decode()

    conn.send(b'ok')

    print(f"Received action {action}")
    filename = conn.recv(CHUNK_SIZE).decode()

    print(f"Received action {action} from addr {addr}. Filename {filename}")
    if action == 'download':
      serve_download(conn, filename)

    if action == 'upload':
      serve_upload(conn, filename)

    #TODO: path absoluto, sacar esto hardcodeado. (El filename se recibe por cliente)

    conn.close()

  sock.close()



def serve_download(conn, filename):
  f = open(filename, "rb")

  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)

  print(f"Found {filename} with size {size}")
  conn.send(str(size).encode())

  signal = conn.recv(CHUNK_SIZE)
  assert signal == b'start'

  while True:
    chunk = f.read(CHUNK_SIZE)
    if not chunk:
      break
    conn.send(chunk)


  print(f"Finished sending {size} bytes")


def serve_upload(conn, filename):
  
  f = open(filename, "wb")
  bytes_received = 0

  size = int(conn.recv(CHUNK_SIZE).decode())
  conn.send(b'start')

  while bytes_received < size:
    data = conn.recv(CHUNK_SIZE)
    bytes_received += len(data)
    f.write(data)

  print("Received file {}".format(filename))

  f.close()