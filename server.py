#! /usr/bin/env python3

import argparse, logging, os, os.path, sys, struct, socket, threading, subprocess, time, signal
from concurrent.futures import ThreadPoolExecutor

# Configurazione dell'indirizzo IP e del numero di porta del server
HOST = "127.0.0.1"  # Indirizzo IP del server
PORT = 56697  # Numero di porta del server
Max_sequence_length = 2048

# Riceve esattamente n byte dal socket conn e li restituisce
# il tipo restituto è "bytes": una sequenza immutabile di valori 0-255
# Questa funzione è analoga alla readn che abbiamo visto nel C
def recv_all(conn,n):
  chunks = b''
  bytes_recd = 0
  while bytes_recd < n:
    chunk = conn.recv(min(n - bytes_recd, 1024))
    if len(chunk) == 0:
      raise RuntimeError("socket connection broken")
    chunks += chunk
    bytes_recd = bytes_recd + len(chunk)
  return chunks

def gestisci_connessione(conn,addr):
  total_byte = 0
  tipo = recv_all(conn,6)      # ricevo il tipo della connessione
  if tipo.decode() == "Tipo A":
    lun_byte = recv_all(conn,4)      # ricevo la lunghezza della stringa che devo leggere
    lun = struct.unpack("!i",lun_byte)[0]
    data = recv_all(conn,lun)
    lun_str = struct.pack("<i",lun)
    total_byte = lun
    # scrivo nella FIFO capolet
    capolet.write(lun_str)
    capolet.write(data)
  else:
    while True:
      lun_byte = recv_all(conn,4)      # ricevo la lunghezza della stringa che devo leggere
      if struct.unpack("!i",lun_byte)[0]==0:
        break
      lun = struct.unpack("!i",lun_byte)[0]
      data = recv_all(conn,lun)
      lun_str = struct.pack("<i",lun)
      # scrivo nella FIFO caposc
      caposc.write(lun_str)
      caposc.write(data)
      total_byte = total_byte + lun
  # scrivo nel file di log il tipo della connessione e i byte scritti nelle FIFO
  logging.info("Connessione di %s, Scritti %d byte",tipo.decode(),total_byte)



def main(p,host=HOST,port=PORT):
  # creiamo il server socket
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    # mi metto in attesa di una connessione
    with ThreadPoolExecutor(argv.arg1) as exe:
      while True:
        try:
          conn, addr = s.accept()
          exe.submit(gestisci_connessione,conn,addr)
        except KeyboardInterrupt:
          signal.signal(signal.SIGINT, signal.SIG_IGN)    # blocco il segnale SIGINT
          signal.signal(signal.SIGTERM, signal.SIG_IGN)    # blocco il segnale SIGTERM
          p.send_signal(signal.SIGTERM)
          caposc.close()
          capolet.close()
          time.sleep(5)
          os.unlink('caposc')
          os.unlink('capolet')
          s.shutdown(socket.SHUT_RDWR)
          signal.signal(signal.SIGINT, signal.default_int_handler)      # sblocco il segnale SIGINT
          signal.signal(signal.SIGTERM, signal.default_int_handler)      # sblocco il segnale SIGTERM
          break
  time.sleep(5)
  s.close()
  # print("---FINE SERVER-----")


# inizio programma prima del main
try:
  # file server.log
  logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
  
  # creazione pipe se non presenti
  if not os.path.exists('caposc'):
    os.mkfifo("caposc")
  elif os.path.isfile('caposc'):    # conntrolla se è un file normale e nel caso lo elimina
    os.remove('caposc')
    os.mkfifo("caposc")
  else:
    os.remove('caposc')
    os.mkfifo("caposc")
  
  if not (os.path.exists('capolet')):
    os.mkfifo("capolet")
  elif os.path.isfile('capolet'):    # conntrolla se è un file normale e nel caso lo elimina
    os.remove('capolet')
    os.mkfifo("capolet")
  else:
    os.remove('capolet')
    os.mkfifo("capolet")
  
  # gestione degli argomenti da linea di comando
  parser = argparse.ArgumentParser()
  parser.add_argument('arg1', type=int)
  parser.add_argument('-r', default='3')
  parser.add_argument('-w', default='3')
  parser.add_argument('-v', action='store_true')
  
  argv = parser.parse_args()
  
  if not argv.v:
    p = subprocess.Popen(["./archivio",argv.r,argv.w])
  else:
    # lanciando anche valgrind
    # print("----------VALGRIND-----------------")
    p = subprocess.Popen(["valgrind","--leak-check=full", "--show-leak-kinds=all", "--log-file=valgrind-%p.log","./archivio",argv.r,argv.w])
  # apro le FIFO in scrittura binaria così posso passare i byte
  caposc = open("caposc", "wb")
  capolet = open("capolet", "wb")
  
  main(p,HOST,PORT)
except KeyboardInterrupt:
  if(p is None):
    p.send_signal(signal.SIGTERM)
  try:
    caposc.close()
    capolet.close()
    time.sleep(5)
    os.unlink('caposc')
    os.unlink('capolet')
  except :
    pass
  