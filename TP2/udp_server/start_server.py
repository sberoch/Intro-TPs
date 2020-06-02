import socket

CHUNK_SIZE = 1024

def start_server(server_address, storage_dir):
  # TODO: Implementar UDP server
  print('UDP: start_server({}, {})'.format(server_address, storage_dir))
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(server_address)

  while True:
    data, addr = sock.recvfrom(CHUNK_SIZE)
    size = int(data.decode())
    print("Incoming file with size {} from {}".format(size, addr))

    #TODO: path absoluto, sacar esto hardcodeado. (El filename se recibe por cliente)
    filename = "asdasd.txt"
    f = open(filename, "wb")
    bytes_received = 0

    sock.sendto(b'start', addr)

    while bytes_received < size:
      data, addr = sock.recvfrom(CHUNK_SIZE)
      bytes_received += len(data)
      f.write(data)

    print("Received file {}".format(filename))

    # Send number of bytes received
    sock.sendto(str(bytes_received).encode(),addr)

    f.close()

  sock.close()

