import socket, subprocess

s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 8888))
s.listen(1)

while True:
    conn, addr = s.accept()
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print "Recv from ", addr, ":", data
        result = subprocess.Popen(data, shell = True, stdout=subprocess.PIPE).communicate()
        if result[1] == None:
            conn.sendall(result[0])
        else:
            print 'Invalid Command'
conn.close()