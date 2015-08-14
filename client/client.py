import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port on the server given by the caller
server_address = (sys.argv[1], 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

while 1:
  try:
      
      #message = 'This is the message.  It will be repeated.'
      #message = 'godzina'
      message = raw_input("msg:")
      print >>sys.stderr, 'sending "%s"' % message
      if not message:
        sock.close()
        break
      #sock.send(chr(len(message)))
      sock.sendall(chr(len(message)) + message)
  
      amount_received = 0
      data_size = sock.recv(1)
      if data_size:
        data_size = ord(data_size)
      else:
        break
      amount_expected = data_size
      total_res = ""
      while amount_received < amount_expected:
          data = sock.recv(1024)
          amount_received += len(data)
          total_res += data
          print >>sys.stderr, 'received "%s"' % data
          if "\0" in data:
            print "got EOT"

  except:
      sock.close()
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect(server_address)

#sock.close()
