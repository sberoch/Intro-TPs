import socket
import os

CHUNK_SIZE = 1024

def start_server(server_address, storage_dir):
  # TODO: Implementar UDP server
  print('UDP: start_server({}, {})'.format(server_address, storage_dir))
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(server_address)

  while True:
    accion, addr = sock.recvfrom(CHUNK_SIZE)
    accion = accion.decode()
    print(accion)
    sock.sendto(b'ok', addr)

    data, addr = sock.recvfrom(CHUNK_SIZE)

    if accion == 'upload':
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

    elif accion == 'download':
      name = data.decode()
      print("Sending file called {} to {}".format(name,addr))

      f = open(name, "rb")
      f.seek(0, os.SEEK_END)
      size = f.tell()
      f.seek(0, os.SEEK_SET)

      sock.sendto(str(size).encode(), addr)

      signal, addr = sock.recvfrom(CHUNK_SIZE)

      if signal.decode() != "start":
        print("There was an error on the server")
        return exit(1)

      while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
          break
        sock.sendto(chunk, addr)

      print('UDP: sent {} bytes'.format(size))


      f.close()

  

  sock.close()

