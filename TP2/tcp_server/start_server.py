import socket, os

CHUNK_SIZE = 1024
DELIMITER = ':'
MAX_TIMEOUT = 5

def start_server(server_address, storage_dir):

  print('TCP: start_server({}, {})'.format(server_address, storage_dir))

  if not os.path.exists(storage_dir):
      print(f"Creating storage_dir at {storage_dir}")
      os.makedirs(storage_dir, exist_ok=True)

  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(50)
  except OSError:
    print(f"Error while creating socket, aborting")
    return exit(1)

  
  try:
    while True:
      print(f"Listening for connections... (press Ctrl+C to exit now)")
      serve_connection(sock, storage_dir)

  except KeyboardInterrupt:
    print("\nExiting!")


  sock.close()


def serve_connection(sock, storage_dir):
  try:
    conn, addr = sock.accept()
    print("=== New connection started")
    if not conn:
      raise ConnectionError
    conn.settimeout(MAX_TIMEOUT)

    print("Accepted connection from {}".format(addr))

    message = conn.recv(CHUNK_SIZE).decode()

    command, info = message.split(DELIMITER, 1)
    print(f"Received action {command} from addr {addr}. File information: {info}")
    
    if command == 'download':
      serve_download(conn, storage_dir, info)

    if command == 'upload':
      serve_upload(conn, storage_dir, info)

    conn.close()
  except (ConnectionError, socket.timeout) as e:
    print(f"\nError while communicating with client, closing connection. Error: {e}")
    return


def serve_download(conn, storage_dir, path):

  full_path = os.path.join(storage_dir, path)


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
  
  if signal != b'start':
    f.close()
    print("Error on client, cancelling transfer")
    return

  print(f"Transfering... (press Ctrl+C to cancel)")
  try:
    while True:
      chunk = f.read(CHUNK_SIZE)
      if not chunk:
        break
      conn.send(chunk)
  except KeyboardInterrupt:
    print("\nCancelled transfer, closing connection...")
    f.close()
    return

  print(f"Finished sending {size} bytes")
  f.close()


def serve_upload(conn, storage_dir, fileinfo):

  filename, size = fileinfo.rsplit(DELIMITER, 1)
  size = int(size)
  
  full_path = os.path.join(storage_dir, filename)
  
  try:
    f = open(full_path, "wb")
  except OSError:
    conn.send(b'error')
    print(f"Error while creating local-file {full_path}, exiting...")
    return

  bytes_received = 0
  conn.send(b'start')

  print(f"Receiving... (press Ctrl+C to cancel)")
  try:
    while bytes_received < size:
      data = conn.recv(CHUNK_SIZE)
      bytes_received += len(data)
      f.write(data)
  except KeyboardInterrupt:
    print("\nCancelled transfer, closing connection...")
    f.close()
    return


  print("Received file {}".format(full_path))

  f.close()