import socket, os

CHUNK_SIZE = 1024

def start_server(server_address, storage_dir):

  print('TCP: start_server({}, {})'.format(server_address, storage_dir))

  if not os.path.exists(storage_dir):
      print(f"Creating storage_dir at {storage_dir}")
      os.makedirs(storage_dir, exist_ok=True)

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind(server_address)
  sock.listen(50)

  print(f"Listening for connections...")
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
    
    full_path = os.path.join(storage_dir, filename)

    if action == 'download':
      serve_download(conn, full_path)

    if action == 'upload':
      serve_upload(conn, full_path)

    conn.close()

  sock.close()



def serve_download(conn, full_path):

  try:
    f = open(full_path, "rb")
  except FileNotFoundError:
    print(f"Requested download for non-existant file {full_path}, aborting connection")
    conn.send(str(-1).encode())
    return

  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)

  print(f"Found {full_path} with size {size}")
  conn.send(str(size).encode())

  signal = conn.recv(CHUNK_SIZE)
  assert signal == b'start'

  while True:
    chunk = f.read(CHUNK_SIZE)
    if not chunk:
      break
    conn.send(chunk)


  print(f"Finished sending {size} bytes")
  f.close()


def serve_upload(conn, full_path):

  conn.send(b'init')
  
  f = open(full_path, "wb")
  bytes_received = 0

  size = int(conn.recv(CHUNK_SIZE).decode())
  conn.send(b'start')

  while bytes_received < size:
    data = conn.recv(CHUNK_SIZE)
    bytes_received += len(data)
    f.write(data)

  print("Received file {}".format(full_path))

  f.close()