import socket

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

    #TODO: path absoluto, sacar esto hardcodeado. (El filename se recibe por cliente)
    filename = "asdasd.txt"
    f = open(filename, "wb")
    bytes_received = 0

    size = int(conn.recv(CHUNK_SIZE).decode())
    conn.send(b'start')

    while bytes_received < size:
      data = conn.recv(CHUNK_SIZE)
      bytes_received += len(data)
      f.write(data)

    print("Received file {}".format(filename))

    # Send number of bytes received
    conn.send(str(bytes_received).encode())

    f.close()

  sock.close()
