import socket
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect(('127.0.0.1', 8888))

while 1:
    cmd = raw_input("zathing>>>").strip()
    if len(cmd) == 0: continue
    c.send(cmd)
    if cmd.split()[0] == 'get':
        print "Starting to download file..."
        with open(cmd.split()[1], 'wb') as f:
            while 1:
                data = c.recv(1024)
                if data == 'FileDone': break
                f.write(data)
                print "."
        continue
    else:
        print c.recv(8096)

c.close()