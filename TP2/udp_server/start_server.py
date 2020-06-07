import socket
import os
import hashlib

CHUNK_SIZE = 1024

def start_server(server_address, storage_dir):
  # TODO: Implementar UDP server

  # Si no existe el storage_dir se crea
  if not os.path.exists(storage_dir):
    print("Creando storage_dir")
    os.makedirs(storage_dir, exist_ok=True)

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
      sock.sendto(b'ok', addr)

      #TODO: path absoluto, sacar esto hardcodeado. (El filename se recibe por cliente)

      data, addr = sock.recvfrom(CHUNK_SIZE)
      filename = data.decode()
      f = open(os.path.join(storage_dir,filename), "wb")
      bytes_received = 0

      sock.sendto(b'start', addr)

      while bytes_received < size:
        data_encoded, addr = sock.recvfrom(CHUNK_SIZE)
        data = data_encoded.decode()
        checksum,data_chunk = data.split(":",1)
        print(data_chunk)
        data_chunk = data_chunk.encode()
        #print(checksum)
        #print(hashlib.md5(data_chunk).hexdigest())
        if (checksum == hashlib.md5(data_chunk).hexdigest()):
          sock.sendto(b'ack', addr)
          bytes_received += len(data_chunk)
          f.write(data_chunk)

      print("Received file {}".format(filename))

      # Send number of bytes received
      sock.sendto(str(bytes_received).encode(),addr)

      f.close()

    elif accion == 'download':
      name = data.decode()
      print("Sending file called {} to {}".format(name, addr))

      path = os.path.join(storage_dir, name)
      if not os.path.exists(path):
        print("File not found")
        sock.sendto("-1".encode(), addr)
        continue

      f = open(path, "rb")
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

      num_bytes, addr = sock.recvfrom(CHUNK_SIZE)
      print('UDP: sent {} bytes'.format(num_bytes.decode()))

      f.close()

  sock.close()
